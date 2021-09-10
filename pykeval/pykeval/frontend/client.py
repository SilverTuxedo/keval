import ctypes
import logging
from pathlib import Path
from typing import List, Tuple

from pykeval.broker.interface import Broker
from pykeval.broker.requests import CallFunction, ReadBytes, WriteBytes
from pykeval.frontend.broker_allocation import BrokerAllocation
from pykeval.frontend.ctypes_shim.native import get_native_type
from pykeval.frontend.ctypes_shim.translate import get_native_pointer_type, TranslatedArgs
from pykeval.frontend.ctypes_shim.utils import is_pointer_type
from pykeval.frontend.function_cache import FunctionCache
from pykeval.frontend.parser import CParser
from pykeval.shared.ffi import FfiArgument

logger = logging.getLogger(__name__)


class Client:
    """
    A client for using a broker.
    """

    def __init__(self, broker: Broker):
        """
        :param broker: The broker the client is based on.
        """

        self.broker = broker
        self._function_cache = FunctionCache()

    def declare_from_header(self, module_name: str, header_path: str) -> List[str]:
        """
        Declare all functions in the given header.

        :param module_name: The name of the module that contains the given functions (without its file prefix).
                            For example, "ntoskrnl.exe" would be "ntoskrnl".
        :param header_path: The path to the header.

        :return: The names of functions that were declared.
        """

        if not Path(header_path).exists():
            raise FileNotFoundError(header_path)

        functions = CParser.get_functions_from_c_header(header_path)
        for func in functions:
            self._function_cache.set(module_name, func)

        assert len(functions) != 0, "No functions were declared"

        return [func.name for func in functions]

    def declare(self, module_name: str, c_declaration: str) -> List[str]:
        """
        Declares all functions in the given C declaration string.

        :param module_name: The name of the module that contains the given functions (without its file prefix).
                            For example, "ntoskrnl.exe" would be "ntoskrnl".
        :param c_declaration: The declaration. For example, "void HelloWorld();"

        :return: The names of functions that were declared.
        """

        functions = CParser.get_functions_from_c_string(c_declaration)

        for func in functions:
            self._function_cache.set(module_name, func)

        assert len(functions) != 0, "No functions were declared"

        return [func.name for func in functions]

    def call(self, module_name: str, function_name: str, *args) -> any:
        """
        Calls a declared function.

        If you get a BSOD after calling this, make sure that your declaration of the function signature was correct.

        :param module_name: The name of the function's module.
        :param function_name: The name of the function.
        :param args: The arguments of the function.

        :return: The function's return value.
        """

        func = self._function_cache.get(module_name, function_name)

        if len(func.arguments) != len(args):
            raise TypeError(f"{func.name}() takes exactly {len(func.arguments)} arguments ({len(args)} given)")

        ffi_args = []
        for named_argument, value in zip(func.arguments, args):
            ffi_args.append(FfiArgument(named_argument.type, value))

        return self.broker.call_function(CallFunction(module_name, func.name, func.return_type, ffi_args))

    def ex_call(self,
                module_name: str,
                function_name: str,
                *args,
                return_type=None,
                read_back_args=True) -> Tuple[any, List, List[BrokerAllocation]]:
        """
        Calls a declared function. This variation supports passing ctypes pointers.

        When passing pointers to structs or other pointers, they may be altered to support the architecture of the
        machine the broker runs on.

        Notice that strings can't be passed directly. They must first be encoded (typically to "ascii" or "utf-16le").
        Make sure that you add a NUL terminator to the string!

        If you get a BSOD after calling this, make sure that your declaration of the function signature was correct
        and that any pointers that you've passed have the correct type.

        :param module_name: The name of the function's module.
        :param function_name: The name of the function.
        :param args: The arguments of the function. They can be either a Python trivial type (int) or a ctypes pointer.
        :param return_type: The type of the return value. If provided, the return value is casted to it. If the type is
                            a ctypes pointer, the return address is read and the *value* of the pointer is returned.
        :param read_back_args: If True, the arguments are read back from the machine before being returned. This is
                               useful for out parameters.

        :return:
            [0] - The return value of the function
            [1] - The arguments that were passed to the machine. If `read_back_args` is True, arguments which were
                  pointers will have the *value* of the pointer.
            [2] - Any allocations that were made for this call
        """

        translated_args = TranslatedArgs(self.broker, *args)
        call_result = self.call(module_name, function_name, *translated_args.args)

        if return_type is not None:
            call_result = self._cast_return_value(call_result, return_type)

        if read_back_args:
            returned_args = translated_args.read_back()
        else:
            returned_args = translated_args.args

        return call_result, returned_args, translated_args.allocations

    def _cast_return_value(self, return_value, return_type) -> any:
        """
        Casts the return value to the return type. This supports ctypes pointers.
        """

        if is_pointer_type(return_type):
            if return_value == 0:
                return None
            native_type = get_native_type(return_type._type_,
                                          get_native_pointer_type(self.broker.get_pointer_size()))
            native_value = native_type()
            data = self.read_bytes(return_value, ctypes.sizeof(native_type))
            ctypes.memmove(ctypes.byref(native_value), data, len(data))
            return native_value
        else:
            return return_type(return_value)

    def read_bytes(self, address: int, size: int) -> bytes:
        """
        Reads bytes from memory on the machine.
        Note that this function does NOT validate the address.

        :param address: The address to read from.
        :param size: The number of bytes to read.

        :return: The data read
        """

        return self.broker.read_bytes(ReadBytes(address, size))

    def read_string(self, address: int) -> str:
        """
        Read a string (char*) from memory on the machine.
        This function continues reading until it encounters a NUL terminator. If the string is malformed, this can cause
        a page fault.

        :param address: The address the string starts at.

        :return: The string.
        """

        return self._read_until(address, b'\0').decode("ascii")

    def read_wstring(self, address: int) -> str:
        """
        Read a string (wchar_t*) from memory on the machine.
        This function continues reading until it encounters a NUL terminator. If the string is malformed, this can cause
        a page fault.

        :param address: The address the string starts at.

        :return: The string.
        """

        return self._read_until(address, b'\0\0').decode("utf-16")

    def _read_until(self, address, terminator: bytes) -> bytes:
        """
        Reads data from the machine until the terminator is found, in multiples of the terminator's size.
        """

        total_data = []
        while (byte := self.read_bytes(address, len(terminator))) != terminator:
            total_data.append(byte)
            address += len(terminator)

        return b"".join(total_data)

    def write_bytes(self, address: int, data: bytes):
        """
        Writes bytes to memory on the machine.
        Note that this function does NOT validate the address.

        :param address: The address to write to.
        :param data: The data to write.
        """
        data = bytes(data)
        return self.broker.write_bytes(WriteBytes(address, data))

    def allocate(self, size: int) -> BrokerAllocation:
        """
        Allocates memory on the machine.

        :param size: The amount of bytes to allocate

        :return: An allocation
        """

        return BrokerAllocation(self.broker, size)
