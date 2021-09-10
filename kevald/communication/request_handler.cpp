#include "request_handler.h"

#include "communication/communication_defs.h"
#include "communication/translate.h"
#include "debug_log.h"
#include "ffi/cif.h"
#include "kernel/nt_exception.h"

namespace keval::communication {

namespace {

/**
    Transforms FfiTypes of a function signature to proper ffi_type pointers.
*/
std::pair<const ffi_type*, Vector<const ffi_type*>> getActualTypes(
    FfiType returnType, const Vector<FfiType>& argumentTypes)
{
    const ffi_type* actualReturnType = translate(returnType);
    Vector<const ffi_type*> actualArgumentTypes;
    actualArgumentTypes.reserve(argumentTypes.size());

    std::ranges::transform(argumentTypes, std::back_inserter(actualArgumentTypes), translate);

    return {actualReturnType, actualArgumentTypes};
}

}  // anonymous namespace

void RequestHandler::handle(RequestCallFunction& request)
{
    // 1. Find the function,
    const auto routineAddress = m_routineFinder.find(request.moduleName, request.functionName);

    auto [returnType, argumentTypes] = getActualTypes(request.returnType, request.argumentTypes);
    ffi::Cif cif(returnType, std::move(argumentTypes));

    // 2. Call the function,
    DEBUG_LOG("Calling %s", request.functionName.c_str());
    auto callResult = cif.call(routineAddress, request.argumentAddresses);
    // Note - if you got a BSOD near this line, it's probably because you declared your function incorrectly.

    // 3. And write the return value back to the user.
    std::ranges::copy(callResult, static_cast<std::byte*>(request.returnValueAddress));
}

void RequestHandler::handle(RequestReadBytes& request)
{
    std::copy_n(request.address, request.outData.size_bytes(), request.outData.data());
}

void RequestHandler::handle(RequestWriteBytes& request)
{
    std::ranges::copy(request.data, request.address);
}

void RequestHandler::handle(RequestAllocate& request)
{
    const auto address = ExAllocatePoolWithTag(NonPagedPool, request.size, config::USER_INITIATED_ALLOCATION_TAG);
    if (nullptr == address) {
        throw kernel::NtException(STATUS_NO_MEMORY);
    }
    RtlZeroMemory(address, request.size);

    *request.outAddress = address;
}

void RequestHandler::handle(RequestFree& request)
{
    ExFreePoolWithTag(request.address, config::USER_INITIATED_ALLOCATION_TAG);
}

}  // namespace keval::communication
