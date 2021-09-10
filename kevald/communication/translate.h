#pragma once
#include <ffi.h>

#include "communication/communication_defs.h"

namespace keval::communication {

class TranslationException : public std::exception
{};
class UnknownValueException : public TranslationException
{};
class UnsupportedValueException : public TranslationException
{};

/**
    Translates an FfiType to a proper ffi_type pointer that can be used in libffi.
*/
ffi_type* translate(FfiType communicationType);

}  // namespace keval::communication
