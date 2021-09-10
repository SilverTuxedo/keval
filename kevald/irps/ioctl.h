#pragma once

constexpr auto KEVALD_DEVICE_TYPE = 0x8000;

enum class IoctlCode
{
    REQUEST = CTL_CODE(KEVALD_DEVICE_TYPE, 0x800, METHOD_NEITHER, FILE_ANY_ACCESS)
};
