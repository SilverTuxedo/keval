#pragma once
#include "exception.h"
#include "kernel/nt_defs.h"

namespace keval::kernel {

/**
    A NTSTATUS exception, typically raised when a kernel API call fails.
*/
class NtException : public Exception
{
public:
    explicit NtException(NTSTATUS status);

    NTSTATUS getErrorCode() const;

private:
    NTSTATUS m_status;
};

/**
    @throws NtException if the status is not successful.
*/
FORCEINLINE void verifyStatus(NTSTATUS status)
{
    if (!NT_SUCCESS(status)) {
        throw NtException(status);
    }
}

}  // namespace keval::kernel
