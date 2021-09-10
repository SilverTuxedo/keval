import ctypes
from dataclasses import dataclass
from typing import Dict

from pykeval.frontend.ctypes_shim.utils import (is_pointer_type, is_struct, get_pointer_address,
                                                get_struct_instance_field_type, STRUCT_FIELD_TYPE_INDEX,
                                                STRUCT_FIELD_NAME_INDEX)


@dataclass
class AlteredField:
    from_type: any
    to_type: any


def get_native_type(data_type, native_pointer_type):
    """
    Gets the type that natively represents the given type.
    This mainly replaces pointers to be their native type. For structs, a new type may be returned.

    :param data_type: A type
    :param native_pointer_type: A type that is able to represent a native pointer.

    :return: The native representation of the given type.
    """

    if is_pointer_type(data_type):
        return native_pointer_type

    if not is_struct(data_type):
        return data_type

    altered_fields = {}
    native_fields = []  # The new fields for the native struct, passed to ctypes
    for existing_field in data_type._fields_:
        field = list(existing_field)

        native_field_type = get_native_type(field[STRUCT_FIELD_TYPE_INDEX], native_pointer_type)
        if native_field_type is not field[STRUCT_FIELD_TYPE_INDEX]:
            field[STRUCT_FIELD_TYPE_INDEX] = native_field_type
            altered_fields[field[STRUCT_FIELD_NAME_INDEX]] = AlteredField(from_type=field[STRUCT_FIELD_TYPE_INDEX],
                                                                          to_type=native_field_type)

        native_fields.append(tuple(field))

    if len(altered_fields) == 0:
        # The native struct is identical. Just return the original one.
        return data_type

    # Declare a new struct with the native fields.
    native_type_attributes = dict(
        _fields_=native_fields,
        _pack_=ctypes.sizeof(native_pointer_type) if not hasattr(data_type, "_pack_") else getattr(data_type, "_pack_"),
        _altered_fields=altered_fields
    )
    native_type = type(data_type.__class__.__name__ + "_NATIVE",
                       (ctypes.Structure,),
                       native_type_attributes)

    return native_type


def get_as_native_value(data, native_type, local_to_native_address_map: Dict[int, int]):
    """
    Copies a value to its native type.

    :param data: The value to copy.
    :param native_type: The native type to copy into.
    :param local_to_native_address_map: A map between {address -> native address}, used to copy pointer values.

    :return: The native value.
    """

    if is_pointer_type(type(data)):
        address = get_pointer_address(data)
        if address in local_to_native_address_map:
            address = local_to_native_address_map[address]

        return native_type(address)

    if not is_struct(data):
        return native_type(data)

    native_value = native_type()
    for field in data._fields_:
        field_name = field[STRUCT_FIELD_NAME_INDEX]
        field_type = field[STRUCT_FIELD_TYPE_INDEX]

        field_value = getattr(data, field_name)
        if field_value is None:
            # Pointers are `None` if they aren't initialized.
            assert is_pointer_type(field_type)
            field_value = 0
        field_native_type = get_struct_instance_field_type(native_value, field_name)

        field_native_value = get_as_native_value(field_value, field_native_type, local_to_native_address_map)
        setattr(native_value, field_name, field_native_value)

    return native_value
