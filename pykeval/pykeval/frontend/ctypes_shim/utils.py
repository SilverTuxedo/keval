import ctypes

"""
Utilities regarding ctypes objects.
"""

STRUCT_FIELD_NAME_INDEX = 0
STRUCT_FIELD_TYPE_INDEX = 1


def is_pointer_type(obj_type):
    try:
        # Cast only works for pointers.
        ctypes.cast(0, obj_type)
        return True
    except TypeError:
        return False


def has_address(obj):
    try:
        ctypes.addressof(obj)
        return True
    except TypeError:
        return False


def get_pointer_address(ptr):
    return ctypes.cast(ptr, ctypes.c_void_p).value or 0


def is_struct(obj):
    return hasattr(obj, "_fields_")


def get_struct_instance_field_type(obj, field_name):
    """
    :param obj: A ctypes struct instance
    :param field_name: A name of a field in the struct

    :return: The declared type of the field
    """

    for field in obj._fields_:
        current_field_name = field[0]
        if current_field_name == field_name:
            return field[1]

    raise KeyError(field_name)
