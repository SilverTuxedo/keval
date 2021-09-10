#include "request_dispatch.h"

#include "communication/buffer_deserializer.h"
#include "communication/communication_defs.h"
#include "communication/deserialize.h"
#include "communication/request_exception.h"
#include "communication/request_handler.h"
#include "debug_log.h"

namespace keval::communication {

void dispatchRequest(const std::span<std::byte>& requestBytes)
{
    RequestHandler handler;
    BufferDeserializer buffer(requestBytes);

    const auto requestType = buffer.read<RequestType>();

    switch (requestType) {
        case RequestType::CALL_FUNCTION: {
            DEBUG_LOG("Got request to call function");
            auto request = deserializeCallFunction(buffer);
            handler.handle(request);
            break;
        }
        case RequestType::READ_BYTES: {
            DEBUG_LOG("Got request to read bytes");
            auto request = deserializeReadBytes(buffer);
            handler.handle(request);
            break;
        }
        case RequestType::WRITE_BYTES: {
            DEBUG_LOG("Got request to write bytes");
            auto request = deserializeWriteBytes(buffer);
            handler.handle(request);
            break;
        }
        case RequestType::ALLOCATE: {
            DEBUG_LOG("Got request to allocate");
            auto request = deserializeAllocate(buffer);
            handler.handle(request);
            break;
        }
         case RequestType::FREE: {
            DEBUG_LOG("Got request to free");
            auto request = deserializeFree(buffer);
            handler.handle(request);
            break;
        }
        default:
            DEBUG_LOG("Unknown request %d", requestType);
            throw UnknownRequestException(requestType);
    }
}

}  // namespace keval::communication
