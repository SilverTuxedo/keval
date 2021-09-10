from argparse import ArgumentParser

from pykeval.broker import LocalBroker, RemoteBrokerServer
from pykeval.broker.remote import DEFAULT_SERVER_PORT
from pykeval.log import setup_root_logger


def main():
    setup_root_logger()

    parser = ArgumentParser(description="Starts a remote broker server for Keval")

    parser.add_argument("-a", "--address", help="The address of the server.", default="0.0.0.0")
    parser.add_argument("-p", "--port", help="The port of the server.", type=int, default=DEFAULT_SERVER_PORT)
    parser.add_argument("-d", "--device", help="The name of the Keval driver's device.", default="\\??\\keval")

    args = parser.parse_args()

    local_broker = LocalBroker(args.device)
    server = RemoteBrokerServer(local_broker, args.address, args.port)
    server.start()
