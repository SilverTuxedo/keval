#pragma once

namespace keval::config {

constexpr int ALLOCATION_TAG = 'lveK'; // Kevl
constexpr int USER_INITIATED_ALLOCATION_TAG = 'UlvK'; // KvlU

constexpr UNICODE_STRING DEVICE_NAME = RTL_CONSTANT_STRING(L"\\Device\\keval");
constexpr UNICODE_STRING DEVICE_SYMBOLIC_LINK = RTL_CONSTANT_STRING(L"\\??\\keval");

}  // namespace keval::config
