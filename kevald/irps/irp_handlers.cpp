#include "irp_handlers.h"

#include <span>

#include "communication/request_dispatch.h"
#include "communication/request_exception.h"
#include "debug_log.h"
#include "ioctl.h"

namespace keval::irp {

namespace {

/**
    Writes a string to the output buffer.
    
    @return The number of bytes written.
*/
size_t writeToOutputBufferSafe(const char* message, const std::span<std::byte>& output)
{
    const auto messageLength = strlen(message);
    const auto maxBytesToWrite = min(output.size(), messageLength + 1);

    std::copy_n(reinterpret_cast<const std::byte*>(message), maxBytesToWrite, output.data());
    return maxBytesToWrite;
}

}  // namespace

NTSTATUS genericCreateClose(PDEVICE_OBJECT, PIRP irp)
{
    irp->IoStatus.Status = STATUS_SUCCESS;
    irp->IoStatus.Information = 0;
    IoCompleteRequest(irp, IO_NO_INCREMENT);
    return STATUS_SUCCESS;
}

NTSTATUS deviceControl(PDEVICE_OBJECT, PIRP irp)
{
    DEBUG_LOG("deviceControl called");
    const auto stack = IoGetCurrentIrpStackLocation(irp);

    const std::span input(
        static_cast<std::byte*>(stack->Parameters.DeviceIoControl.Type3InputBuffer),
        stack->Parameters.DeviceIoControl.InputBufferLength);

    const std::span output(
        static_cast<std::byte*>(irp->UserBuffer),
        stack->Parameters.DeviceIoControl.OutputBufferLength);

    const auto ioctlCode = static_cast<IoctlCode>(stack->Parameters.DeviceIoControl.IoControlCode);

    NTSTATUS status = STATUS_UNSUCCESSFUL;
    size_t bytesWritten = 0;

    try {
        switch (ioctlCode) {
            case IoctlCode::REQUEST:
                try {
                    communication::dispatchRequest(input);
                    status = STATUS_SUCCESS;
                } catch (const communication::UnknownRequestException& e) {
                    status = STATUS_INVALID_DEVICE_REQUEST;
                    DEBUG_LOG("%s", e.what());
                    bytesWritten = writeToOutputBufferSafe(e.what(), output);
                }
                break;
            default:
                status = STATUS_INVALID_DEVICE_REQUEST;
        }
    } catch (const Exception& e) {
        status = STATUS_UNSUCCESSFUL;
        DEBUG_LOG("%s", e.what());
        bytesWritten = writeToOutputBufferSafe(e.what(), output);
    } catch (const std::bad_alloc&) {
        status = STATUS_NO_MEMORY;
        bytesWritten = writeToOutputBufferSafe("Not enough memory", output);
    }

    irp->IoStatus.Status = status;
    irp->IoStatus.Information = bytesWritten;
    IoCompleteRequest(irp, IO_NO_INCREMENT);
    return status;
}
}  // namespace keval::irp
