#pragma once
#include <span>

#include "communication/deserialize_exception.h"

namespace keval::communication {

/**
    Wraps a buffer for easy serialization.
*/
class BufferDeserializer
{
public:
    explicit BufferDeserializer(const std::span<std::byte>& source, size_t startPosition = 0);

    /**
        Reads the given type from the buffer and advances the position.
    */
    template <typename T>
    T read();

    /**
        Advance the buffer position `count` bytes, without returning anything.
    */
    void ignore(size_t count);

    std::byte* getPosition() const;

    size_t bytesLeft() const;

private:
    std::byte* m_position;
    const std::byte* m_end;
};

template <typename T>
T BufferDeserializer::read()
{
    auto* newPosition = m_position + sizeof(T);
    if (newPosition > m_end) {
        throw DeserializeException();
    }

    const T value = *reinterpret_cast<T*>(m_position);

    m_position = newPosition;
    return value;
}

}  // namespace keval::communication
