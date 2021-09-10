#pragma once
#include <span>

#include "alias.h"

namespace keval::communication {

enum class RequestType : uint8_t
{
    INVALID = 0,
    CALL_FUNCTION,
    READ_BYTES,
    WRITE_BYTES,
    ALLOCATE,
    FREE
};

enum class FfiType : uint8_t
{
    VOID_ = 0,
    UINT8,
    SINT8,
    UINT16,
    SINT16,
    UINT32,
    SINT32,
    UINT64,
    SINT64,
    FLOAT,
    DOUBLE,
    UCHAR,
    SCHAR,
    USHORT,
    SSHORT,
    UINT,
    SINT,
    ULONG,
    SLONG,
    POINTER
};

/**
    A request to call a function.
*/
struct RequestCallFunction
{
    String moduleName;
    String functionName;
    FfiType returnType;
    Vector<FfiType> argumentTypes;
    void* returnValueAddress;
    Vector<void*> argumentAddresses;
};

struct RequestReadBytes
{
    std::byte* address;
    std::span<std::byte> outData;
};

struct RequestWriteBytes
{
    std::byte* address;
    std::span<std::byte> data;
};

struct RequestAllocate
{
    uint32_t size;
    void** outAddress;
};

struct RequestFree
{
    void* address;
};

}  // namespace keval::communication
