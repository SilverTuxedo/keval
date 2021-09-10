#include "alias.h"
#include "config.h"
#include "final_action.h"
#include "globals.h"
#include "irps/irp_handlers.h"
#include "kernel/nt_exception.h"

namespace keval {

Globals* g_globals;

/**
    Initializes the device of the driver and properly sets it in the global.

    @throws NtException if the device could not be initialized.
*/
void initializeDevice(DRIVER_OBJECT& driverObject)
{
    PDEVICE_OBJECT rawDeviceObject = nullptr;
    auto status = IoCreateDevice(
        &driverObject,
        0,
        const_cast<UNICODE_STRING*>(&config::DEVICE_NAME),
        FILE_DEVICE_UNKNOWN,
        0,
        FALSE,
        &rawDeviceObject);
    kernel::verifyStatus(status);

    kernel::UniqueDeviceObject deviceObject(rawDeviceObject);

    status = IoCreateSymbolicLink(
        const_cast<UNICODE_STRING*>(&config::DEVICE_SYMBOLIC_LINK), const_cast<UNICODE_STRING*>(&config::DEVICE_NAME));
    kernel::verifyStatus(status);

    g_globals->device = std::move(deviceObject);
    g_globals->symbolicLink.reset(&config::DEVICE_SYMBOLIC_LINK);
}

void driverUnload(PDRIVER_OBJECT)
{
    if (nullptr != g_globals) {
        g_globals->~Globals();
        operator delete(g_globals, NonPagedPool, config::ALLOCATION_TAG);
    }
}

extern "C" NTSTATUS DriverEntry(PDRIVER_OBJECT driverObject, PUNICODE_STRING)
{
    driverObject->DriverUnload = driverUnload;

    try {
        g_globals = new (NonPagedPool, config::ALLOCATION_TAG) Globals();
    } catch (const std::bad_alloc&) {
        return STATUS_NO_MEMORY;
    }

    FinalAction cleanup([=] { driverUnload(driverObject); });

    try {
        initializeDevice(*driverObject);
    } catch (const kernel::NtException& exception) {
        return exception.getErrorCode();
    }

    driverObject->MajorFunction[IRP_MJ_CREATE] = irp::genericCreateClose;
    driverObject->MajorFunction[IRP_MJ_CLOSE] = irp::genericCreateClose;
    driverObject->MajorFunction[IRP_MJ_DEVICE_CONTROL] = irp::deviceControl;

    cleanup.cancel();
    return STATUS_SUCCESS;
}

}  // namespace keval
