#pragma once

#include "communication/buffer_deserializer.h"
#include "communication/communication_defs.h"

namespace keval::communication {

RequestCallFunction deserializeCallFunction(BufferDeserializer& data);

RequestReadBytes deserializeReadBytes(BufferDeserializer& data);

RequestWriteBytes deserializeWriteBytes(BufferDeserializer& data);

RequestAllocate deserializeAllocate(BufferDeserializer& data);

RequestFree deserializeFree(BufferDeserializer& data);

}
