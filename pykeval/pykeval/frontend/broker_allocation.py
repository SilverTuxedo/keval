import logging

from pykeval.broker.interface import Broker
from pykeval.broker.requests import Allocate, Free, ReadBytes, WriteBytes

logger = logging.getLogger(__name__)


class BrokerAllocation:
    """
    Represents an allocation by a broker. This object attempts to free the memory once it is garbage collected.
    """

    def __init__(self, broker: Broker, address_or_size: int, size: int = None):
        """
        Either creates a new allocation using the broker or wraps an existing allocation.

        :param broker: The broker the allocation is done through
        :param address_or_size: If `size` is None, the size of the new allocation to make.
                                Otherwise, the address of the existing allocation.
        :param size: The size of the existing allocation (if `address_or_size` is the address).
        """

        self.broker = broker
        if size is None:
            self._size = address_or_size
            self._allocation = broker.allocate(Allocate(self._size))
        else:
            self._size = size
            self._allocation = address_or_size

    @property
    def address(self):
        return self._allocation

    def __len__(self):
        return self._size

    def read(self) -> bytes:
        assert self._allocation is not None
        return self.broker.read_bytes(ReadBytes(self._allocation, self._size))

    def write(self, data: bytes, offset: int = 0):
        assert self._allocation is not None

        if offset >= self._size:
            raise ValueError(f"Offset {offset} is too great, only {self._size} bytes available")

        available_size = self._size - offset
        if len(data) > available_size:
            raise ValueError(f"Data length is too great, only {available_size} bytes available (attempted {len(data)})")

        self.broker.write_bytes(WriteBytes(self._allocation + offset, data))

    def free(self):
        if self._allocation is not None:
            logger.info(f"Freeing allocation {self._allocation}")
            self.broker.free(Free(self._allocation))
        self._allocation = None
        self._size = 0

    def __del__(self):
        self.free()
