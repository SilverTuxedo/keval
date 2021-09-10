import logging

from pykeval.shared.ffi import FfiFunction

logger = logging.getLogger(__name__)


class FunctionCache:
    """
    A cache for FFI function declarations.
    """

    def __init__(self):
        self._cache = {}

    def set(self, module_name: str, func: FfiFunction):
        if module_name not in self._cache:
            self._cache[module_name] = {}

        cache = self._cache[module_name]
        is_override = func.name in cache

        cache[func.name] = func
        if is_override:
            logger.info(f"Updated declaration of {module_name}!{func.name}")

    def get(self, module_name: str, function_name: str) -> FfiFunction:
        return self._cache[module_name][function_name]

    def exists(self, module_name: str, function_name: str) -> bool:
        try:
            self.get(module_name, function_name)
            return True
        except KeyError:
            return False
