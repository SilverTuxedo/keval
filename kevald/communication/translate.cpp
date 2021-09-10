#include "translate.h"

#include "debug_log.h"

namespace keval::communication {
ffi_type* translate(FfiType communicationType)
{
    switch (communicationType) {
        case FfiType::VOID_:
            return &ffi_type_void;
        case FfiType::UINT8:
            return &ffi_type_uint8;
        case FfiType::SINT8:
            return &ffi_type_sint8;
        case FfiType::UINT16:
            return &ffi_type_uint16;
        case FfiType::SINT16:
            return &ffi_type_sint16;
        case FfiType::UINT32:
            return &ffi_type_uint32;
        case FfiType::SINT32:
            return &ffi_type_sint32;
        case FfiType::UINT64:
            return &ffi_type_uint64;
        case FfiType::SINT64:
            return &ffi_type_sint64;
        case FfiType::FLOAT:
            throw UnsupportedValueException();
        case FfiType::DOUBLE:
            throw UnsupportedValueException();
        case FfiType::UCHAR:
            return &ffi_type_uchar;
        case FfiType::SCHAR:
            return &ffi_type_schar;
        case FfiType::USHORT:
            return &ffi_type_ushort;
        case FfiType::SSHORT:
            return &ffi_type_sshort;
        case FfiType::UINT:
            return &ffi_type_uint;
        case FfiType::SINT:
            return &ffi_type_sint;
        case FfiType::ULONG:
            return &ffi_type_ulong;
        case FfiType::SLONG:
            return &ffi_type_slong;
        case FfiType::POINTER:
            return &ffi_type_pointer;
    }

    DEBUG_LOG("Unable to translate unknown FFI type %d", communicationType);
    throw UnknownValueException();
}

}  // namespace keval::communication
