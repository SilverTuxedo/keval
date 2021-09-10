import logging
import pickle
from socketserver import BaseRequestHandler, TCPServer

from pykeval.broker.local import LocalBroker
from pykeval.broker.requests import BrokerResponse, BrokerResponseType, BrokerRequest, BrokerRequestType
from pykeval.broker.messaging import receive, send

logger = logging.getLogger(__name__)


class BrokerRequestHandler(BaseRequestHandler):
    broker_server = None

    def handle(self) -> None:
        logger.info(f"Got connection from {self.client_address}")

        data = receive(self.request)
        logger.debug("Received")
        try:
            request = pickle.loads(data)
            # noinspection PyProtectedMember
            response_data = self.__class__.broker_server._on_new_request(request)
            response = BrokerResponse(BrokerResponseType.SUCCESS, response_data)
        except Exception as e:
            logger.exception("Error processing request")
            response = BrokerResponse(BrokerResponseType.EXCEPTION, e)

        logger.debug("Serializing and sending response")
        serialized_response = pickle.dumps(response)
        send(self.request, serialized_response)
        logger.info(f"Sent response to {self.client_address}")


class RemoteBrokerServer:
    """
    A broker server based on a local broker over TCP. This works together with `RemoteBroker` to allow running code on a
    different machine than the client itself.
    """

    def __init__(self, local_broker: LocalBroker, address: str, port: int):
        """
        :param local_broker: The actual local broker that will handle requests
        :param address: The address of the server
        :param port: The port of the server
        """

        self._local_broker = local_broker
        self._address = address
        self._port = port

    def start(self):
        """
        Starts the TCP server.
        """

        handler_type = type("BoundBrokerRequestHandler", (BrokerRequestHandler,), {"broker_server": self})
        with TCPServer((self._address, self._port), handler_type) as server:
            logger.info(f"Starting server at {self._address}:{self._port}")
            server.serve_forever()

    def _on_new_request(self, request: BrokerRequest):
        """
        Handles a broker request.

        :return: What the local broker returned for the request
        :raises ValueError if the request type is not supported.
        """

        # No-data requests
        if request.type == BrokerRequestType.GET_POINTER_SIZE:
            return self._local_broker.get_pointer_size()

        # Data requests
        try:
            handler = {
                BrokerRequestType.CALL_FUNCTION: self._local_broker.call_function,
                BrokerRequestType.READ_BYTES: self._local_broker.read_bytes,
                BrokerRequestType.WRITE_BYTES: self._local_broker.write_bytes,
                BrokerRequestType.ALLOCATE: self._local_broker.allocate,
                BrokerRequestType.FREE: self._local_broker.free
            }[request.type]

            return handler(request.data)
        except KeyError:
            pass

        raise ValueError(f"Unrecognized request type {request.type.value}")
