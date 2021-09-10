import ctypes
import struct
from enum import Enum, auto
from io import BytesIO

import pykeval.broker.requests as broker_requests
from pykeval.broker.ioctl import METHOD_NEITHER, FILE_ANY_ACCESS
from pykeval.broker.ioctl_serialize import (serialize_enum_value, serialize_string, serialize_enum_array,
                                            serialize_pointer, serialize_array, serialize_buffer_view)
from pykeval.shared.ffi import FFI_TYPE_TO_CTYPES_TYPE_MAP

"""
Constants and definitions for communicating with the driver using IOCTL.

Ioctl requests usually contain ctypes - that is so the driver can respond to the request by writing
directly to Python and not through the output buffer. This allows more flexibility regarding the sizes of
request results.
"""


def ctl_code(device_type, function, method, access):
    return (device_type << 16) | (access << 14) | (function << 2) | method


KEVALD_DEVICE_TYPE = 0x8000
MESSAGE_IOCTL_CODE = ctl_code(KEVALD_DEVICE_TYPE, 0x800, METHOD_NEITHER, FILE_ANY_ACCESS)


class IoctlRequestType(Enum):
    INVALID = 0
    CALL_FUNCTION = auto()
    READ_BYTES = auto()
    WRITE_BYTES = auto()
    ALLOCATE = auto()
    FREE = auto()


class IoctlCallFunction:
    def __init__(self, request: broker_requests.CallFunction):
        self.module_name = request.module_name
        self.function_name = request.function_name

        self.ffi_return_type = request.return_type
        ctypes_return_type = FFI_TYPE_TO_CTYPES_TYPE_MAP[self.ffi_return_type]
        if ctypes_return_type is None:
            self.return_value = ctypes.c_void_p(0)
        else:
            self.return_value = ctypes_return_type()

        self.ffi_argument_types = [arg.type for arg in request.arguments]
        self.arguments = []
        for python_arg in request.arguments:
            ctypes_arg = FFI_TYPE_TO_CTYPES_TYPE_MAP[python_arg.type](python_arg.value)
            self.arguments.append(ctypes_arg)

    def serialize(self):
        buffer = BytesIO()

        serialize_enum_value(buffer, IoctlRequestType.CALL_FUNCTION)
        serialize_string(buffer, self.module_name)
        serialize_string(buffer, self.function_name)
        serialize_enum_value(buffer, self.ffi_return_type)
        serialize_enum_array(buffer, self.ffi_argument_types)
        serialize_pointer(buffer, ctypes.addressof(self.return_value))
        serialize_array(buffer, [ctypes.addressof(arg) for arg in self.arguments], "P")

        buffer.seek(0)
        return bytes(buffer.read())


class IoctlReadBytes:
    def __init__(self, request: broker_requests.ReadBytes):
        self.address = request.address
        self.result_buffer = ctypes.create_string_buffer(request.size)

    def serialize(self):
        buffer = BytesIO()

        serialize_enum_value(buffer, IoctlRequestType.READ_BYTES)
        serialize_pointer(buffer, self.address)
        serialize_buffer_view(buffer, self.result_buffer)

        buffer.seek(0)
        return bytes(buffer.read())


class IoctlWriteBytes:
    def __init__(self, request: broker_requests.WriteBytes):
        self.address = request.address
        self.buffer = ctypes.create_string_buffer(request.data, len(request.data))

    def serialize(self):
        buffer = BytesIO()

        serialize_enum_value(buffer, IoctlRequestType.WRITE_BYTES)
        serialize_pointer(buffer, self.address)
        serialize_buffer_view(buffer, self.buffer)

        buffer.seek(0)
        return bytes(buffer.read())


class IoctlAllocate:
    def __init__(self, request: broker_requests.Allocate):
        self.size = request.size
        self.result = ctypes.c_size_t(0)

    def serialize(self):
        buffer = BytesIO()

        serialize_enum_value(buffer, IoctlRequestType.ALLOCATE)
        buffer.write(struct.pack("I", self.size))
        serialize_pointer(buffer, ctypes.addressof(self.result))

        buffer.seek(0)
        return bytes(buffer.read())


class IoctlFree:
    def __init__(self, request: broker_requests.Free):
        self.address = request.address

    def serialize(self):
        buffer = BytesIO()

        serialize_enum_value(buffer, IoctlRequestType.FREE)
        serialize_pointer(buffer, self.address)

        buffer.seek(0)
        return bytes(buffer.read())


