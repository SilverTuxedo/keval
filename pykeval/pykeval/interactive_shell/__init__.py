from IPython import embed

import pykeval.broker
import pykeval.log
import pykeval.server
from pykeval.frontend import Client


def get_local_client(*args, **kwargs):
    broker = pykeval.broker.LocalBroker(*args, **kwargs)
    return Client(broker)


def get_remote_client(*args, **kwargs):
    broker = pykeval.broker.RemoteBroker(*args, **kwargs)
    return Client(broker)


def start_interactive_shell():
    pykeval.log.setup_root_logger()

    embed(header="\n".join((
        "Welcome to Keval's interactive client shell!",
        "",
        "To get a client, you can use:",
        "* `get_local_client()`: If the driver is running on this machine",
        "* `get_remote_client()`: If you want to connect to a remote machine "  # Note: no comma continues line
        "(also see the console command `keval-server`)"
    )))
