#pragma once
#include "exception.h"

namespace keval::routines {

class RoutineNotFoundException : public Exception
{
public:
    explicit RoutineNotFoundException(const String& routineName);
};

class ModuleNotFoundException : public Exception
{
public:
    explicit ModuleNotFoundException(const String& moduleName);
};

}  // namespace keval::routines
