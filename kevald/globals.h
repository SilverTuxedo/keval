#pragma once
#include "kernel/nt_objects.h"

namespace keval {

struct Globals
{
    kernel::UniqueDeviceObject device;
    kernel::UniqueSymbolicLink symbolicLink;
};

// Any code that runs after the DriverEntry and before DriverUnload can assume this pointer is valid.
extern Globals* g_globals;

}  // namespace keval
