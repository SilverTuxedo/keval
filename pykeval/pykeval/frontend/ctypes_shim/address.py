import ctypes

_POINTER_SIZE_32BIT = 4


def get_is_kernel_address(pointer_size: int):
    """
    :return: A function that determines if an address resides in the kernel space.
    """

    if pointer_size == _POINTER_SIZE_32BIT:
        # 32 bit machines *can* have a user-space of 3GB, however this is not so common. If this is ever an issue,
        # this function will be updated.
        def is_kernel_address(address: int):
            return address < 0x80000000
    else:
        def is_kernel_address(address: int):
            return 0 != (address & 0xFF00000000000000)

    return is_kernel_address


def get_is_valid_usermode_address(is_kernel_address_func):
    """
    :param is_kernel_address_func: A function that determines if an address is in kernel space.
    :return: A function that determines if a given address is valid in user space.
    """

    def is_valid_usermode_address(address: int):
        is_kernel = is_kernel_address_func(address)
        return not is_kernel and 0 != address
    return is_valid_usermode_address


def get_native_pointer_type(pointer_size: int):
    """
    :return: A type that can represent a pointer.
    """

    return {
        ctypes.sizeof(ctypes.c_uint32): ctypes.c_uint32,
        ctypes.sizeof(ctypes.c_uint64): ctypes.c_uint64,
    }[pointer_size]
