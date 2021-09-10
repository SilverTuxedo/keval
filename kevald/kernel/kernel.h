#pragma once
#include <optional>
#include <system_error>

#include "alias.h"
#include "kernel/nt_defs.h"

namespace keval {
namespace kernel {

/**
    @return The base address of nt.
*/
const void* getKernelBase();

/**
    Finds a kernel-space routine.

    @param kernelModuleBase The base address of the module exporting the routine.
    @param routineName The name of the export.

    @return The address of the export, or `nullopt` if not found.
*/
std::optional<const void*> findRoutine(const void* kernelModuleBase, const char* routineName);

/**
    Finds a kernel module's address by name.
    The name is checked without the file suffix, meaning that in order to find "ntoskrnl.exe" one should pass
   "ntoskrnl". The search is case-insensitive.

    @return The base address of the module, or `nullopt` if not found.
*/
std::optional<const void*> getModuleBase(const String& moduleName);

}  // namespace kernel

/**
    Wrapper for ZwQuerySystemInformation. See:
    https://docs.microsoft.com/en-us/windows/win32/sysinfo/zwquerysysteminformation
*/
NTSTATUS NTAPI ZwQuerySystemInformation(
    SYSTEM_INFORMATION_CLASS SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength,
    PULONG ReturnLength);
;
}  // namespace keval
