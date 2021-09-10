#pragma once
#include "kernel/nt_defs.h"

#if defined(DEBUG)
#define DEBUG_LOG(format, ...) DbgPrint("[*] %s@%d: " format "\n", __FUNCTION__, __LINE__, __VA_ARGS__)
#else
#define DEBUG_LOG(...)
#endif
