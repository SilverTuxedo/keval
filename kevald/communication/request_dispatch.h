#pragma once
#include <span>

#include "kernel/nt_defs.h"

namespace keval::communication {

/**
    Dispatches a generic request to the correct request handler.

    @param requestBytes The raw request.

    @throw UnknownRequestException
*/
void dispatchRequest(const std::span<std::byte>& requestBytes);

}  // namespace keval::communication
