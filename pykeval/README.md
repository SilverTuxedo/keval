

# pykeval

pykeval is the user mode portion of the **Keval** project. It allows communication with Keval's driver (`kevald.sys`).

The package defines a few console scripts:

* `keval-server`: Starts a `RemoteBrokerServer` on the machine. This is what you need to run on the machine you want to run code on (if it is not your machine).
* `ikeval`: Interactive Python shell (based on IPython) for a quick start.

When installing the package on the machine you want to work on, make sure to pass the `client` extra to pip:

```
pip install pykeval[client]
```

