import ctypes
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class FfiType(Enum):
    VOID = 0
    UINT8 = auto()
    SINT8 = auto()
    UINT16 = auto()
    SINT16 = auto()
    UINT32 = auto()
    SINT32 = auto()
    UINT64 = auto()
    SINT64 = auto()
    FLOAT = auto()
    DOUBLE = auto()
    UCHAR = auto()
    SCHAR = auto()
    USHORT = auto()
    SSHORT = auto()
    UINT = auto()
    SINT = auto()
    ULONG = auto()
    SLONG = auto()
    POINTER = auto()


@dataclass
class FfiArgument:
    """
    Function(1024);
    ---------^^^^
    """
    type: FfiType
    value: any


@dataclass
class FfiNamedArgument:
    """
    void Function(int x);
    --------------^^^^^
    """
    type: FfiType
    name: str


@dataclass
class FfiFunction:
    name: str
    return_type: FfiType
    arguments: List[FfiNamedArgument]


FFI_TYPE_TO_CTYPES_TYPE_MAP = {
    FfiType.VOID: None,
    FfiType.UINT8: ctypes.c_uint8,
    FfiType.SINT8: ctypes.c_int8,
    FfiType.UINT16: ctypes.c_uint16,
    FfiType.SINT16: ctypes.c_int16,
    FfiType.UINT32: ctypes.c_uint32,
    FfiType.SINT32: ctypes.c_int32,
    FfiType.UINT64: ctypes.c_uint64,
    FfiType.SINT64: ctypes.c_int64,
    FfiType.FLOAT: ctypes.c_float,
    FfiType.DOUBLE: ctypes.c_double,
    FfiType.UCHAR: ctypes.c_ubyte,
    FfiType.SCHAR: ctypes.c_char,
    FfiType.USHORT: ctypes.c_ushort,
    FfiType.SSHORT: ctypes.c_short,
    FfiType.UINT: ctypes.c_uint,
    FfiType.SINT: ctypes.c_int,
    FfiType.ULONG: ctypes.c_ulong,
    FfiType.SLONG: ctypes.c_long,
    FfiType.POINTER: ctypes.c_void_p
}
