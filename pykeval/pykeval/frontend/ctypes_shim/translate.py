import ctypes
from dataclasses import dataclass
from typing import Tuple, List

from pykeval.frontend.broker_allocation import BrokerAllocation
from pykeval.frontend.ctypes_shim.address import (get_native_pointer_type, get_is_valid_usermode_address,
                                                  get_is_kernel_address)
from pykeval.frontend.ctypes_shim.collect import gather_pointers
from pykeval.frontend.ctypes_shim.native import get_native_type, get_as_native_value
from pykeval.frontend.ctypes_shim.utils import get_pointer_address, is_pointer_type


@dataclass
class PointerTranslationContext:
    """
    Describes a translation of a pointer to a native pointer.
    """

    allocation: BrokerAllocation
    local_pointer: any
    native_pointed_type: any


class TranslatedArgs:
    def __init__(self, broker, *args):
        """
        Translates arguments so they can be used natively on the broker's machine.

        :param broker: A broker.
        :param args: The arguments to translate.
        """

        pointer_size = broker.get_pointer_size()

        self._translated_args = []

        self._broker = broker
        self._native_pointer_type = get_native_pointer_type(pointer_size)
        self._is_valid_address = get_is_valid_usermode_address(get_is_kernel_address(pointer_size))

        for arg in args:
            self._translated_args.append(self._translate_argument(arg))

    def _translate_argument(self, arg) -> Tuple[any, List[PointerTranslationContext]]:
        contexts = []

        if isinstance(arg, str):
            raise TypeError("Strings are not directly supported, please encode them.")

        if isinstance(arg, bytes):
            return self._translate_bytes(arg)

        if not is_pointer_type(type(arg)):
            # Currently translating only pointers, passing structs directly is not supported.
            return arg, []

        # 1. Collect all pointers this argument refers to (including itself).
        pointers = gather_pointers(arg, self._is_valid_address)

        # 2. Create allocations of appropriate (native) size for each pointer's contents.
        allocations = []  # (ctypes ptr, allocation, native type)
        for pointer in pointers:
            contents_native_type = get_native_type(pointer._type_, self._native_pointer_type)
            allocation = BrokerAllocation(self._broker, ctypes.sizeof(contents_native_type))
            allocations.append((pointer, allocation, contents_native_type))

        flat_address_map = {get_pointer_address(ptr): allocation.address for ptr, allocation, _ in allocations}

        # 3. Copy the values to the new (native) allocations
        for pointer, allocation, native_type in allocations:
            native_value = get_as_native_value(pointer.contents, native_type, flat_address_map)
            assert len(allocation) == ctypes.sizeof(native_value)
            allocation.write(ctypes.string_at(ctypes.addressof(native_value), len(allocation)))

            contexts.append(PointerTranslationContext(allocation, pointer, native_type))

        # Since the argument must be a pointer to reach here, and we have allocated for it, use the map to return its
        # allocated kernel address
        arg_address = flat_address_map[get_pointer_address(arg)]

        return arg_address, contexts

    def _translate_bytes(self, data: bytes) -> Tuple[int, List[PointerTranslationContext]]:
        allocation = BrokerAllocation(self._broker, len(data))
        allocation.write(data)

        return allocation.address, [PointerTranslationContext(allocation=allocation,
                                                              local_pointer=None,
                                                              native_pointed_type=ctypes.c_byte * len(data))]

    @property
    def args(self):
        """
        :return: The translated arguments.
        """

        return [value for value, contexts in self._translated_args]

    @property
    def allocations(self):
        """
        :return: All of the allocations that were made to translate the arguments.
        """

        result = []
        for value, contexts in self._translated_args:
            result.extend(context.allocation for context in contexts)

        return result

    def read_back(self):
        """
        Reads back the allocations that were made for each argument.

        :return: The values of the arguments. For pointer arguments, the value of the pointer.
        """

        values = []

        for arg, contexts in self._translated_args:
            value = arg
            for context in contexts:
                if context.allocation.address == arg:
                    data = context.allocation.read()
                    value = context.native_pointed_type()
                    ctypes.memmove(ctypes.byref(value), data, len(data))
                    break

            values.append(value)

        return values
