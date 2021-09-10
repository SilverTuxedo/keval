#include "deserialize.h"

#include "alias.h"
#include "communication/deserialize_exception.h"

/*
For some reason, it appears that this translation unit somehow includes a header that
defines a dynamic initializer for `locale::id_std::numpunct<char>::id`.

The best lead appears to be this:
https://gitmemory.com/issue/microsoft/STL/1926/845673319
It looks like this dynamic initializer was added in Visual Studio 16.10 (I am writing
this in 16.11).

I am ignoring dynamic initializer warnings (/IGNORE:4210) until this is resolved
by Microsoft, so help me god.
*/

namespace keval::communication {

namespace {

String deserializeString(BufferDeserializer& data)
{
    const auto size = data.read<uint8_t>();
    if (size > data.bytesLeft()) {
        throw DeserializeException();
    }

    auto* stringEnd = reinterpret_cast<char*>(data.getPosition() + size);
    String result(reinterpret_cast<char*>(data.getPosition()), stringEnd);
    data.ignore(size);

    return result;
}

template <typename T>
Vector<T> deserializeArray(BufferDeserializer& data)
{
    const auto size = data.read<uint8_t>();
    if (size > data.bytesLeft() * sizeof(T)) {
        throw DeserializeException();
    }

    Vector<T> result;
    result.reserve(size);
    for (size_t i = 0; i < size; ++i) {
        result.push_back(data.read<T>());
    }

    return result;
}

std::span<std::byte> deserializeBufferView(BufferDeserializer& data)
{
    const auto address = data.read<std::byte*>();
    const auto size = data.read<uint32_t>();

    return std::span(address, size);
}

}  // namespace

RequestCallFunction deserializeCallFunction(BufferDeserializer& data)
{
    return RequestCallFunction{
        .moduleName = deserializeString(data),
        .functionName = deserializeString(data),
        .returnType = data.read<FfiType>(),
        .argumentTypes = deserializeArray<FfiType>(data),
        .returnValueAddress = data.read<void*>(),
        .argumentAddresses = deserializeArray<void*>(data)};
}

RequestReadBytes deserializeReadBytes(BufferDeserializer& data)
{
    return RequestReadBytes{.address = data.read<std::byte*>(), .outData = deserializeBufferView(data)};
}

RequestWriteBytes deserializeWriteBytes(BufferDeserializer& data)
{
    return RequestWriteBytes{.address = data.read<std::byte*>(), .data = deserializeBufferView(data)};
}

RequestAllocate deserializeAllocate(BufferDeserializer& data)
{
    return RequestAllocate{.size = data.read<uint32_t>(), .outAddress = data.read<void**>()};
}

RequestFree deserializeFree(BufferDeserializer& data)
{
    return RequestFree{.address = data.read<void*>()};
}

}  // namespace keval::communication
