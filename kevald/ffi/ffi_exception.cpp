#include "ffi_exception.h"

namespace keval::ffi {

char const* BadAbiException::what() const
{
    return "FFI exception: Bad ABI";
}

char const* BadTypedefException::what() const
{
    return "FFI exception: Bad type definition";
}

}  // namespace keval::ffi
