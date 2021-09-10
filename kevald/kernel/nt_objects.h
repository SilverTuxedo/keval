#pragma once
#include <memory>

#include "kernel/nt_defs.h"

namespace keval::kernel {

/**
    RAII Wrappers for NT objects.
*/

struct DeviceDeleter
{
    void operator()(DEVICE_OBJECT* device) const noexcept;
};

struct SymbolicLinkDeleter
{
    void operator()(const UNICODE_STRING* symlink) const noexcept;
};

using UniqueDeviceObject = std::unique_ptr<DEVICE_OBJECT, DeviceDeleter>;
using UniqueSymbolicLink = std::unique_ptr<const UNICODE_STRING, SymbolicLinkDeleter>;

}  // namespace keval::kernel
