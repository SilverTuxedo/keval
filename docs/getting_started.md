# Getting started

## Building kevald.sys

1. Generate the appropriate `.vcxproj` for libffi. Make sure you have `cmake` and `py` installed and run:

```
kevald/libffi/make.bat
```

2. Build `kevald/kevald.sln`. It should emit the driver under `out/<architecture>/<configuration>/kevald.sys`.

## Setting up a remote machine

Both the local and remote machine should have Python **3.8** or greater.

* Compile the driver under `kevald/`. (**keval d**river)
* Copy the driver to the machine you want to execute kernel-mode code on.
* Install and run the driver:

```
sc create kevald type= kernel binPath= <path to driver>
sc start kevald
```

* Install the `pykeval` package using `pip` on the remote machine and run the server using this command line:

```
keval-server [address] [port]
```

* Install the `pykeval` package on the local machine with the `client` extra (`pip install pykeval[client]`).
* Set up the client to use a `RemoteBroker`.

```python
client = pykeval.frontend.Client(pykeval.broker.RemoteBroker(<address>[, port]))
```

## Setting up on a local machine

If you want to run code on the same machine where your client resides, you can do that by passing `LocalBroker` instead of `RemoteBroker` and skip the server.

