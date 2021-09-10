#pragma once
/*

This header should be included instead of any Windows headers to prevent typedef conflicts.
It also defines some undocumented APIs.

*/

#include <fltKernel.h>

extern "C" PVOID NTAPI RtlPcToFileHeader(PVOID PcValue, PVOID* BaseOfImage);
extern "C" PVOID NTAPI RtlFindExportedRoutineByName(PVOID DllBase, PCHAR RoutineName);

typedef struct _RTL_PROCESS_MODULE_INFORMATION
{
    HANDLE Section;
    PVOID MappedBase;
    PVOID ImageBase;
    ULONG ImageSize;
    ULONG Flags;
    USHORT LoadOrderIndex;
    USHORT InitOrderIndex;
    USHORT LoadCount;
    USHORT OffsetToFileName;
    UCHAR FullPathName[256];
} RTL_PROCESS_MODULE_INFORMATION, *PRTL_PROCESS_MODULE_INFORMATION;

typedef struct _RTL_PROCESS_MODULES
{
    ULONG NumberOfModules;
    RTL_PROCESS_MODULE_INFORMATION Modules[1];
} RTL_PROCESS_MODULES, *PRTL_PROCESS_MODULES;

enum class SYSTEM_INFORMATION_CLASS
{
    SystemModuleInformation = 0xB
};
