import ctypes

from pykeval.frontend import Client
from pykeval.broker import RemoteBroker


class UNICODE_STRING(ctypes.Structure):
    _fields_ = [
        ("Length", ctypes.c_ushort),
        ("MaximumLength", ctypes.c_ushort),
        ("Buffer", ctypes.c_wchar_p)
    ]


client = Client(RemoteBroker("192.168.233.156"))
temp = UNICODE_STRING()

# We declare the signature of `RtlInitUnicodeString` like we'd do in a C header. Note that we don't actually
# need to declare `struct UNICODE_STRING` because we're passing a pointer.
client.declare("ntoskrnl",
               "void RtlInitUnicodeString(UNICODE_STRING* DestinationString, wchar_t* SourceString);")

return_value, args, allocations = client.ex_call("ntoskrnl",
                                                 "RtlInitUnicodeString",
                                                 ctypes.pointer(temp),  # This is an out param
                                                 "Hello\0".encode("UTF-16LE"),
                                                 read_back_args=True)

# We don't need the allocations that were made during this call since we read back the arguments.
for allocation in allocations:
    allocation.free()
# BrokerAllocation objects are also garbage-collected by Python, but it's best not to rely on that.

out_param = args[0]
# The type of `out_param` has the same fields as `UNICODE_STRING` but `Buffer` was converted to a type
# compatible with the broker's machine (in case of a 64-bit machine, `c_uint64`).
# Since read_back_args=True, the type of the argument is the *value* of the pointer after the call.
assert "Hello" == client.read_wstring(out_param.Buffer)
