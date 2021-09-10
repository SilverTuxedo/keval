from abc import ABC, abstractmethod

from pykeval.broker.requests import CallFunction, ReadBytes, WriteBytes, Allocate, Free


class Broker(ABC):
    """
    A broker is responsible for communicating with the driver on the target machine.
    It services the client (which may be on another machine).
    """

    @abstractmethod
    def get_pointer_size(self) -> int:
        """
        :return: The size of a pointer on the target machine.
        """

        pass

    @abstractmethod
    def call_function(self, request_data: CallFunction) -> any:
        """
        Calls a kernel-mode function on target machine.

        :return: The return value of the function.
        """

        pass

    @abstractmethod
    def read_bytes(self, request_data: ReadBytes) -> bytes:
        """
        Reads kernel-mode memory from the target machine.

        :return: The data read.
        """
        pass

    @abstractmethod
    def write_bytes(self, request_data: WriteBytes):
        """
        Writes to the kernel-mode memory of the target machine.
        Note that this does not allocate memory, it writes to existing allocations.
        """

        pass

    @abstractmethod
    def allocate(self, request_data: Allocate) -> int:
        """
        Allocates kernel-mode memory.
        The resulting allocation will read-write-execute permissions.

        :return The address of the allocation
        """

        pass

    @abstractmethod
    def free(self, request_data: Free):
        """
        Frees previously allocates kernel-mode memory from `allocate()`.
        """

        pass
