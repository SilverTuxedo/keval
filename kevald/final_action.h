#pragma once
#include <concepts>

namespace keval {

/**
    Calls the given callable once this object is destroyed.
*/
template <std::invocable T>
class FinalAction
{
public:
    explicit FinalAction(T f) noexcept : m_callable(std::move(f)), m_shouldInvoke(true) {}

    FinalAction(FinalAction&& other) noexcept
        : m_callable(std::move(other.m_callable))
        , m_shouldInvoke(other.m_shouldInvoke)
    {
        other.m_shouldInvoke = false;
    }

    FinalAction(const FinalAction&) = delete;
    FinalAction& operator=(const FinalAction&) = delete;

    ~FinalAction() noexcept
    {
        if (m_shouldInvoke) {
            std::invoke(m_callable);
        }
    }

    void cancel()
    {
        m_shouldInvoke = false;
    }

private:
    T m_callable;
    bool m_shouldInvoke;
};

}  // namespace keval
