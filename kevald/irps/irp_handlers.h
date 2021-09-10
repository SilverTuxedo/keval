#pragma once
#include "kernel/nt_defs.h"

namespace keval::irp {

/**
    A handler shared by both create and close - simply succeeds.
*/
NTSTATUS genericCreateClose(PDEVICE_OBJECT deviceObject, PIRP irp);

NTSTATUS deviceControl(PDEVICE_OBJECT deviceObject, PIRP irp);

}  // namespace keval::irp
