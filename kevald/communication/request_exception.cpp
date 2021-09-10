#include "request_exception.h"

#include "format.h"

namespace keval::communication {

UnknownRequestException::UnknownRequestException(RequestType type) : RequestException()
{
    try {
        setReason(String("Unknown request type ") + toHex(static_cast<uint8_t>(type)));
    } catch (const std::bad_alloc&) {
        // intentionally blank
    }
}

}  // namespace keval::communication
