import logging
from typing import List

from clang.cindex import Index, Cursor, TypeKind, Type, TranslationUnit

from pykeval.shared.ffi import FfiType, FfiFunction, FfiNamedArgument

logger = logging.getLogger(__name__)


class CParser:
    """
    Parser of C headers.
    """

    @staticmethod
    def get_functions_from_c_header(header_file_path) -> List[FfiFunction]:
        index = Index.create()
        translation_unit = index.parse(header_file_path, options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
        root = translation_unit.cursor

        return CParser._translation_unit_to_ffi_functions(root)

    @staticmethod
    def get_functions_from_c_string(c_string: str) -> List[FfiFunction]:
        index = Index.create()
        translation_unit = index.parse("header.hpp",
                                       unsaved_files=[("header.hpp", c_string)],
                                       options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
        root = translation_unit.cursor

        return CParser._translation_unit_to_ffi_functions(root)

    @staticmethod
    def _translation_unit_to_ffi_functions(root: Cursor) -> List[FfiFunction]:
        functions = []
        for node in root.get_children():  # TODO: does this need to be recursive?
            try:
                if node.kind.name != "FUNCTION_DECL":
                    continue

                functions.append(CParser._create_ffi_function(node))
            except Exception:
                logger.exception(f"Exception during parsing of {node.location.file}:{node.location.line}")
                raise

        return functions

    @staticmethod
    def _create_ffi_function(cursor: Cursor) -> FfiFunction:
        name = cursor.spelling
        canonical_return_type = cursor.result_type.get_canonical()
        arguments = cursor.get_arguments()

        ffi_return_type = translate_clang_type_to_ffi_type(canonical_return_type)
        ffi_arguments = []
        for cursor in arguments:
            canonical_type = cursor.type.get_canonical()
            ffi_type = translate_clang_type_to_ffi_type(canonical_type)
            ffi_arguments.append(FfiNamedArgument(ffi_type, cursor.spelling))

        return FfiFunction(name, ffi_return_type, ffi_arguments)


_CLANG_TYPE_TO_FFI_TYPE_MAP = {
    TypeKind.ATOMIC: FfiType.POINTER,  # Assuming atomic is sized as size_t
    TypeKind.BOOL: FfiType.UINT8,
    TypeKind.CHAR_S: FfiType.SCHAR,
    TypeKind.CHAR_U: FfiType.UCHAR,
    TypeKind.CHAR16: FfiType.UINT16,
    TypeKind.CHAR32: FfiType.UINT32,
    TypeKind.DOUBLE: FfiType.DOUBLE,
    TypeKind.FLOAT: FfiType.FLOAT,
    TypeKind.INT: FfiType.SINT,
    TypeKind.LONG: FfiType.SLONG,
    TypeKind.LONGLONG: FfiType.SINT64,  # Assuming MSVC
    TypeKind.NULLPTR: FfiType.POINTER,
    TypeKind.POINTER: FfiType.POINTER,
    TypeKind.SCHAR: FfiType.SCHAR,
    TypeKind.SHORT: FfiType.SSHORT,
    TypeKind.UCHAR: FfiType.UCHAR,
    TypeKind.UINT: FfiType.UINT,
    TypeKind.ULONG: FfiType.ULONG,
    TypeKind.ULONGLONG: FfiType.UINT64,  # Assuming MSVC
    TypeKind.USHORT: FfiType.USHORT,
    TypeKind.VOID: FfiType.VOID,
    TypeKind.WCHAR: FfiType.UINT16  # Assuming MSVC
}


def translate_clang_type_to_ffi_type(clang_type: Type) -> FfiType:
    """
    :raises KeyError if the clang type can't be represented as an FFI type.
    """

    if clang_type.kind not in _CLANG_TYPE_TO_FFI_TYPE_MAP:
        message = f"Type '{clang_type.spelling}' could not be resolved ({clang_type.kind})"
        if clang_type.kind is TypeKind.RECORD:
            message += ". Please note that struct definitions are currently not supported."

        raise KeyError(message)

    return _CLANG_TYPE_TO_FFI_TYPE_MAP[clang_type.kind]
