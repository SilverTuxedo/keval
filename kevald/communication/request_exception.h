#pragma once
#include "communication/communication_defs.h"
#include "exception.h"

namespace keval::communication {

class RequestException : public Exception
{};

class UnknownRequestException : public RequestException
{
public:
    explicit UnknownRequestException(RequestType type);
};

}  // namespace keval::communication
