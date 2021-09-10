#pragma once
#include <exception>

#include <ffi.h>

#include "exception.h"
#include "kernel/nt_defs.h"

namespace keval::ffi {

class FfiException : public Exception
{};

class BadAbiException : public FfiException
{
public:
    char const* what() const override;
};

class BadTypedefException : public FfiException
{
public:
    char const* what() const override;
};

/**
    @throws FfiException if the status is not successful.
*/
FORCEINLINE void verifyStatus(ffi_status status)
{
    switch (status) {
        case FFI_OK:
            return;
        case FFI_BAD_TYPEDEF:
            throw BadTypedefException();
        case FFI_BAD_ABI:
            throw BadAbiException();
    }
}

}  // namespace keval::ffi
