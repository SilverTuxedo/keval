#pragma once
#include <exception>

namespace keval::communication {

class DeserializeException : public std::exception
{
public:
    explicit DeserializeException() = default;
};

}  // namespace keval::communication
