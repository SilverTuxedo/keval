#include "cif.h"

#include "ffi/ffi_exception.h"

namespace keval::ffi {

Cif::Cif(const ffi_type* returnType, Vector<const ffi_type*>&& argumentTypes, ffi_abi abi)
    : m_cif{}
    , m_argumentTypes(std::move(argumentTypes))
{
    auto status = ffi_prep_cif(
        &m_cif,
        abi,
        static_cast<unsigned int>(m_argumentTypes.size()),
        const_cast<ffi_type*>(returnType),
        const_cast<ffi_type**>(m_argumentTypes.data()));

    verifyStatus(status);
}

Buffer Cif::call(const void* function, const std::span<void*>& argumentAddresses)
{
    auto expectedReturnSize = m_cif.rtype->size;
    if (0 != expectedReturnSize) {
        expectedReturnSize =
            max(expectedReturnSize, sizeof(ffi_arg));  // Satisfy libffi size requirement for return value
    }

    Buffer returnBuffer;
    returnBuffer.resize(expectedReturnSize);

    ffi_call(&m_cif, (void (*)())function, returnBuffer.data(), argumentAddresses.data());

    returnBuffer.resize(m_cif.rtype->size);  // Resize to the actual size the user expects
    return returnBuffer;
}
}  // namespace keval::ffi
