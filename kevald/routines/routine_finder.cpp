#include "routine_finder.h"

#include "kernel/kernel.h"
#include "routine_exception.h"

namespace keval::routines {

const void* RoutineFinder::find(const String& moduleName, const String& routineName)
{
    const auto moduleBase = kernel::getModuleBase(moduleName);
    if (!moduleBase.has_value()) {
        throw ModuleNotFoundException(moduleName);
    }

    const auto routine = kernel::findRoutine(moduleBase.value(), routineName.c_str());
    if (!routine.has_value()) {
        throw RoutineNotFoundException(routineName);
    }

    return routine.value();
}

}  // namespace keval::routines
