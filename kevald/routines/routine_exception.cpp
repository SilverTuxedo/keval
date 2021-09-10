#include "routine_exception.h"

namespace keval::routines {

RoutineNotFoundException::RoutineNotFoundException(const String& routineName) : Exception()
{
    try {
        setReason(String("Routine ") + routineName + " was not found");
    } catch (const std::bad_alloc&) {
        // intentionally blank
    }
}

ModuleNotFoundException::ModuleNotFoundException(const String& moduleName)
{
    try {
        setReason(String("Module ") + moduleName + " was not found");
    } catch (const std::bad_alloc&) {
        // intentionally blank
    }
}

}  // namespace keval::routines
