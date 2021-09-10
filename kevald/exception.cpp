#include "exception.h"

namespace keval {

Exception::Exception() {}

Exception::Exception(String reason) : m_reason(std::move(reason)) {}

void Exception::setReason(String reason)
{
    m_reason = std::move(reason);
}

char const* Exception::what() const
{
    if (m_reason.has_value()) {
        return m_reason->c_str();
    }

    return "Unknown reason";
}

}  // namespace keval
