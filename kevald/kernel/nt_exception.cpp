#include "nt_exception.h"

#include "format.h"

namespace keval::kernel {

NtException::NtException(NTSTATUS status) : Exception(), m_status(status)
{
    try {
        setReason(String("NT error ") + toHex(status));
    } catch (const std::bad_alloc&) {
        // intentionally blank
    }
}

NTSTATUS NtException::getErrorCode() const
{
    return m_status;
}

}  // namespace keval::kernel
