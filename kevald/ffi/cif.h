#pragma once
#include <span>

#include <ffi.h>

#include "alias.h"

namespace keval::ffi {

/**
    A Call InterFace for calling an arbitrary function. Backed by libffi.
*/
class Cif
{
public:
    /**
        @throws FfiException if the parameters are malformed.
    */
    Cif(const ffi_type* returnType, Vector<const ffi_type*>&& argumentTypes, ffi_abi abi = FFI_DEFAULT_ABI);

    /**
        Calls the function according to the Cif declaration.

        @param function The address of the function to call.
        @param argumentAddresses Pointers to each argument of the function.

        @return Whatever the function returned. In case of a `void` return type, the buffer is empty.
    */
    Buffer call(const void* function, const std::span<void*>& argumentAddresses);

private:
    ffi_cif m_cif;
    Vector<const ffi_type*> m_argumentTypes;
};

}  // namespace keval::ffi
