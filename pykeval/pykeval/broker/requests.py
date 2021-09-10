from dataclasses import dataclass
from enum import Enum
from typing import List

from pykeval.shared.ffi import FfiType, FfiArgument

"""
Definitions for communication with a broker server.
"""


class BrokerRequestType(Enum):
    GET_POINTER_SIZE = 0
    CALL_FUNCTION = 1
    READ_BYTES = 2
    WRITE_BYTES = 3
    ALLOCATE = 4
    FREE = 5


class BrokerResponseType(Enum):
    SUCCESS = 0
    EXCEPTION = 1


@dataclass
class BrokerRequest:
    type: BrokerRequestType
    data: any


@dataclass
class BrokerResponse:
    type: BrokerResponseType
    data: any


@dataclass
class CallFunction:
    module_name: str
    function_name: str
    return_type: FfiType
    arguments: List[FfiArgument]


@dataclass
class ReadBytes:
    address: int
    size: int


@dataclass
class WriteBytes:
    address: int
    data: bytes


@dataclass
class Allocate:
    size: int


@dataclass
class Free:
    address: int
