#include "nt_objects.h"

namespace keval::kernel {

void DeviceDeleter::operator()(DEVICE_OBJECT* device) const noexcept
{
    IoDeleteDevice(device);
}

void SymbolicLinkDeleter::operator()(const UNICODE_STRING* symlink) const noexcept
{
    IoDeleteSymbolicLink(const_cast<UNICODE_STRING*>(symlink));
}

}  // namespace keval::kernel
