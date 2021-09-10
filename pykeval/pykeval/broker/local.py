import ctypes

from pykeval.broker.interface import Broker
from pykeval.broker.ioctl import DeviceIoControl
from pykeval.broker.ioctl_requests import IoctlCallFunction, IoctlReadBytes, IoctlWriteBytes, MESSAGE_IOCTL_CODE, \
    IoctlAllocate, IoctlFree
from pykeval.broker.requests import CallFunction, ReadBytes, WriteBytes, Allocate, Free


class LocalBroker(Broker):
    """
    A broker that communicates using IOCTLs to the driver on the local machine.
    """

    def __init__(self, device_name: str = "\\??\\keval"):
        """
        :param device_name: The name of the driver's device to which IOCTLs will be sent.
        """

        self.device_name = device_name

    def get_pointer_size(self) -> int:
        return ctypes.sizeof(ctypes.c_void_p)

    def call_function(self, request_data: CallFunction) -> any:
        ioctl_request = IoctlCallFunction(request_data)
        self._send_ioctl(ioctl_request)
        return ioctl_request.return_value.value

    def read_bytes(self, request_data: ReadBytes) -> bytes:
        ioctl_request = IoctlReadBytes(request_data)
        self._send_ioctl(ioctl_request)
        return ioctl_request.result_buffer.raw

    def write_bytes(self, request_data: WriteBytes):
        ioctl_request = IoctlWriteBytes(request_data)
        self._send_ioctl(ioctl_request)

    def allocate(self, request_data: Allocate):
        ioctl_request = IoctlAllocate(request_data)
        self._send_ioctl(ioctl_request)
        return ioctl_request.result.value

    def free(self, request_data: Free):
        ioctl_request = IoctlFree(request_data)
        self._send_ioctl(ioctl_request)

    def _send_ioctl(self, request, output_buffer_size=0x100):
        """
        Sends a request to the device.
        Note that the IOCTL may modify the data inside the request.
        """

        python_buffer = request.serialize()

        input_buffer = ctypes.create_string_buffer(python_buffer, len(python_buffer))
        output_buffer = ctypes.create_string_buffer(output_buffer_size)
        with DeviceIoControl(self.device_name) as device:
            success, bytes_returned = device.ioctl(MESSAGE_IOCTL_CODE,
                                                   input_buffer,
                                                   ctypes.sizeof(input_buffer),
                                                   output_buffer,
                                                   ctypes.sizeof(output_buffer))
        assert success, output_buffer.value
