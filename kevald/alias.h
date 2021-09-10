#pragma once

#include <jxy/locks.hpp>
#include <jxy/map.hpp>
#include <jxy/string.hpp>
#include <jxy/vector.hpp>

#include "config.h"

namespace keval {

template <typename T, POOL_TYPE poolType = PagedPool>
using Vector = jxy::vector<T, poolType, config::ALLOCATION_TAG>;

using Buffer = Vector<std::byte>;
using NonPagedBuffer = jxy::vector<std::byte, NonPagedPoolNx, config::ALLOCATION_TAG>;

using String = jxy::string<PagedPool, config::ALLOCATION_TAG>;

using Mutex = jxy::mutex<config::ALLOCATION_TAG>;

template <typename TKey, typename T, POOL_TYPE poolType = PagedPool>
using Map = jxy::map<TKey, T, poolType, config::ALLOCATION_TAG>;

}  // namespace keval
