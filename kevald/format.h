#pragma once
#include "alias.h"

namespace keval {

template <typename Num>
String toHex(Num num, size_t stringSize = sizeof(Num) << 1)
{
    constexpr char DIGITS[] = "0123456789ABCDEF";

    String result(stringSize, '0');

    for (size_t i = 0, j = (stringSize - 1) * 4; i < stringSize; ++i, j -= 4) {
        result[i] = DIGITS[(num >> j) & 0x0f];
    }
    return result;
}

}  // namespace keval
