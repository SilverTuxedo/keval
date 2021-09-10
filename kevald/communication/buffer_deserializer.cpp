#include "buffer_deserializer.h"

namespace keval::communication {

BufferDeserializer::BufferDeserializer(const std::span<std::byte>& source, size_t startPosition)
    : m_position(source.data() + startPosition)
    , m_end(source.data() + source.size_bytes())
{}

void BufferDeserializer::ignore(size_t count)
{
    auto* newPosition = m_position + count;
    if (newPosition > m_end) {
        throw DeserializeException();
    }

    m_position = newPosition;
}

std::byte* BufferDeserializer::getPosition() const
{
    return m_position;
}

size_t BufferDeserializer::bytesLeft() const
{
    return m_end - m_position;
}

}  // namespace keval::communication
