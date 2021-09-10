import ctypes
import struct
from io import BytesIO

"""
Utilities for serializing data for IOCTLs. 
"""


class SerializationError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __str__(self):
        return self.reason


def _serialize_to_ascii(string: str) -> bytes:
    try:
        return bytes(string, "ascii")
    except UnicodeEncodeError as e:
        raise SerializationError(f"Function name '{string}' cannot be represented in ASCII") from e


def serialize_string(buffer: BytesIO, string: str):
    ascii_string = _serialize_to_ascii(string)
    buffer.write(struct.pack("B", len(ascii_string)))
    buffer.write(ascii_string)


def serialize_enum_value(buffer: BytesIO, enum_entry):
    buffer.write(struct.pack("B", enum_entry.value))


def serialize_pointer(buffer: BytesIO, pointer):
    buffer.write(struct.pack("P", pointer))


def serialize_array(buffer: BytesIO, array, array_type):
    buffer.write(struct.pack("B", len(array)))
    buffer.write(struct.pack(array_type * len(array), *array))


def serialize_enum_array(buffer: BytesIO, array):
    serialize_array(buffer, list(element.value for element in array), "B")


def serialize_buffer_view(buffer: BytesIO, ctypes_buffer):
    serialize_pointer(buffer, ctypes.addressof(ctypes_buffer))
    buffer.write(struct.pack("I", ctypes.sizeof(ctypes_buffer)))
