#pragma once
#include "alias.h"

namespace keval::routines {

class RoutineFinder
{
public:
    /**
        Finds a kernel-space routine.

        @param moduleName The base address of the module exporting the routine.
        @param routineName The name of the routine.

        @return The address of the routine.

        @throws RoutineNotFoundException
        @throws ModuleNotFoundException
    */
    const void* find(const String& moduleName, const String& routineName);
};

}  // namespace keval::routines
