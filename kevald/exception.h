#pragma once
#include <exception>

#include "alias.h"

namespace keval {

class Exception : public std::exception
{
public:
    Exception();
    explicit Exception(String reason);

    void setReason(String reason);

    char const* what() const override;

private:
    std::optional<String> m_reason;
};

}  // namespace keval
