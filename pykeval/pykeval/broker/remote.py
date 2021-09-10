import logging
import pickle
import socket
from functools import lru_cache

from pykeval.broker.interface import Broker
from pykeval.broker.requests import BrokerResponse, BrokerResponseType, BrokerRequest, BrokerRequestType
from pykeval.broker.messaging import send, receive

logger = logging.getLogger(__name__)

DEFAULT_SERVER_PORT = 16350


def _wrap_and_send(request_type: BrokerRequestType):
    def impl(self, request_data=None):
        return self._send_request(BrokerRequest(request_type, request_data))

    return impl


class RemoteBroker(Broker):
    """
    A proxy to a broker server over TCP. This is useful when you want the actual broker to be on another machine.
    See `RemoteBrokerServer`
    """

    def __init__(self, address: str, port: int = DEFAULT_SERVER_PORT):
        """
        :param address: The address of the broker server
        :param port: The port of the broker server
        """

        self.server_address = address
        self.server_port = port

    @lru_cache
    def get_pointer_size(self) -> int:
        return _wrap_and_send(BrokerRequestType.GET_POINTER_SIZE)(self)

    call_function = _wrap_and_send(BrokerRequestType.CALL_FUNCTION)
    read_bytes = _wrap_and_send(BrokerRequestType.READ_BYTES)
    write_bytes = _wrap_and_send(BrokerRequestType.WRITE_BYTES)
    allocate = _wrap_and_send(BrokerRequestType.ALLOCATE)
    free = _wrap_and_send(BrokerRequestType.FREE)

    def _send_request(self, request: BrokerRequest) -> any:
        """
        Sends a request to the remote broker server and returns its response.

        :raises ValueError if the response from the broker couldn't be interpreted.
        """

        data = pickle.dumps(request)
        serialized_response = self._communicate(data)
        response = pickle.loads(serialized_response)  # type: BrokerResponse

        if response.type is BrokerResponseType.EXCEPTION:
            raise response.data  # Exception was raised on the remote broker. Try viewing its logs for more info.
        elif response.type is BrokerResponseType.SUCCESS:
            return response.data
        raise ValueError(f"Got unknown response type from remote broker: {response.type}")

    def _communicate(self, data: bytes) -> bytes:
        """
        Sends data to the server and returns its response.
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            logger.debug(f"Connecting with f{self.server_address}:{self.server_port}")
            sock.connect((self.server_address, self.server_port))
            send(sock, data)
            logger.debug(f"Waiting for response")
            return receive(sock)
