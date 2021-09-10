from collections import Iterable

from pykeval.frontend.ctypes_shim.utils import is_pointer_type, get_pointer_address, is_struct, STRUCT_FIELD_NAME_INDEX


def gather_pointers(root_object, is_valid_address, state=None) -> Iterable:
    """
    Recursively gathers ctypes pointers under the given object (containing itself).

    :param root_object: The object to scan for pointers.
    :param is_valid_address: A predicate that determines if an address should be dereferenced.
    :param state: An internal state of the function. You should not set this value yourself.

    :return: The gathered pointers.
    """

    if state is None:
        state = {}

    if is_pointer_type(type(root_object)):
        address = get_pointer_address(root_object)

        if not is_valid_address(address) or address in state:
            return state.values()

        state[address] = root_object
        return gather_pointers(root_object.contents, is_valid_address, state)

    if not is_struct(root_object):
        return state.values()

    for field in root_object._fields_:
        field_name = field[STRUCT_FIELD_NAME_INDEX]
        field_value = getattr(root_object, field_name)
        gather_pointers(field_value, is_valid_address, state)

    return state.values()
