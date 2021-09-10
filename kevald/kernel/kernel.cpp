#include "kernel.h"

#include "kernel/nt_exception.h"

namespace keval {
namespace kernel {

namespace {

/**
    @param fullPathName A full path.
    @param moduleName A name of a module without its file type (".sys").

    @return true if the the path belongs to the module.
*/
bool isModuleInFullPathName(const std::string_view& fullPathName, const std::string_view& moduleName)
{
    constexpr char ALLOWED_PREFIXES[] = {'/', '\\'};
    constexpr char ALLOWED_SUFFIXES[] = {'.'};

    const auto moduleNameIndex = fullPathName.rfind(moduleName);
    if (String::npos == moduleNameIndex) {
        return false;
    }

    const bool prefixOk = (0 == moduleNameIndex)
        || std::ranges::any_of(ALLOWED_PREFIXES, [&](char allowedPrefix) {
            return fullPathName[moduleNameIndex - 1] == allowedPrefix;
        });

    if (!prefixOk) {
        return false;
    }

    const bool suffixOk = (fullPathName.length() - moduleName.length() == moduleNameIndex)
        || std::ranges::any_of(ALLOWED_SUFFIXES, [&](char allowedSuffix) {
            return fullPathName[moduleNameIndex + moduleName.length()] == allowedSuffix;
        });

    return suffixOk;
}

/**
    toupper, but using the proper types.
*/
char charToupper(char c)
{
    return static_cast<char>(::toupper(c));
}

}  // anonymous namespace

const void* getKernelBase()
{
    UNICODE_STRING functionName = RTL_CONSTANT_STRING(L"RtlPcToFileHeader");
    void* kernelFunctionAddress = MmGetSystemRoutineAddress(&functionName);

    void* result = nullptr;
    // Note: can't use RtlPcToFileHeader as a parameter because the linker may not link directly to it.
    RtlPcToFileHeader(kernelFunctionAddress, &result);

    return result;
}

std::optional<const void*> findRoutine(const void* kernelModuleBase, const char* routineName)
{
    const auto address =
        RtlFindExportedRoutineByName(const_cast<void*>(kernelModuleBase), const_cast<char*>(routineName));
    if (nullptr == address) {
        return std::nullopt;
    }
    return address;
}

std::optional<const void*> getModuleBase(const String& moduleName)
{
    String moduleNameUppercase = moduleName;
    std::ranges::transform(moduleNameUppercase, moduleNameUppercase.begin(), charToupper);

    constexpr auto INITIAL_BUFFER_SIZE = 0x1000;
    auto retries = 9;

    NonPagedBuffer buffer(INITIAL_BUFFER_SIZE);
    ULONG returnLength = 0;
    NTSTATUS status = STATUS_UNSUCCESSFUL;

    do {
        if (status == STATUS_INFO_LENGTH_MISMATCH) {
            buffer.resize(buffer.size() * 2);
        }

        status = ZwQuerySystemInformation(
            SYSTEM_INFORMATION_CLASS::SystemModuleInformation,
            buffer.data(),
            static_cast<ULONG>(buffer.size()),
            &returnLength);
    } while (--retries > 0 && status == STATUS_INFO_LENGTH_MISMATCH);

    verifyStatus(status);

    auto header = reinterpret_cast<PRTL_PROCESS_MODULES>(buffer.data());
    for (size_t i = 0; i < header->NumberOfModules; ++i) {
        auto& mod = header->Modules[i];

        // Make sure the module name is properly null terminated for long module names.
        UCHAR& nullTerminator = mod.FullPathName[_countof(mod.FullPathName) - 1];
        if (nullTerminator != '\0') {
            nullTerminator = '\0';
        }

        String fullPathName(reinterpret_cast<char*>(mod.FullPathName));
        std::ranges::transform(fullPathName, fullPathName.begin(), charToupper);

        if (isModuleInFullPathName(fullPathName, moduleNameUppercase)) {
            return mod.ImageBase;
        }
    }

    return std::nullopt;
}

}  // namespace kernel

NTSTATUS ZwQuerySystemInformation(
    SYSTEM_INFORMATION_CLASS SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength,
    PULONG ReturnLength)
{
    using Func_t = decltype(&ZwQuerySystemInformation);
    static std::optional<Func_t> cache;

    if (!cache.has_value()) {
        UNICODE_STRING functionName = RTL_CONSTANT_STRING(L"ZwQuerySystemInformation");
        const auto address = MmGetSystemRoutineAddress(&functionName);
        if (nullptr == address) {
            throw kernel::NtException(STATUS_NOT_FOUND);
        }

        cache = reinterpret_cast<Func_t>(address);
    }

    return cache.value()(SystemInformationClass, SystemInformation, SystemInformationLength, ReturnLength);
}

}  // namespace keval
