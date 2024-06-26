from typing import Callable, TypeVar, cast, Protocol
from functools import wraps


class AutosaveProtocol(Protocol):
    _autosave_on_change: bool
    _autosave_enabled: bool

    def enable_autosave(self) -> None:
        # fmt: off
        ...
        # fmt: on

    def disable_autosave(self) -> None:
        # fmt: off
        ...
        # fmt: on


T = TypeVar("T", bound=Callable[..., None])


def toggle_autosave_on(func: T) -> T:
    """
    A decorator that specifically toggles the autosave feature on before and off after calling the decorated function.

    This is useful for functions that change the settings and should autosave the settings after the function is called.
    Be aware toggling the autosave feature can be expensive, as each nested `ChangeDetectingDict` and `ChangeDetectingList` gets updated.
    The target function must be an instance method part of a class that implements `enable_autosave` and `disable_autosave` methods,
    as well as two boolean attributes `_autosave_on_change` and `_autosave_enabled`.
    """

    @wraps(wrapped=func)
    def wrapper(self: AutosaveProtocol, *args, **kwargs) -> None:
        if self._autosave_on_change and not self._autosave_enabled:
            self.enable_autosave()

        func(self, *args, **kwargs)

        if self._autosave_on_change and self._autosave_enabled:
            self.disable_autosave()

    return cast(T, wrapper)


def toggle_autosave_off(func: T) -> T:
    """
    A decorator that specifically toggles the autosave feature off before and on after calling the decorated function.
    """

    @wraps(wrapped=func)
    def wrapper(self: AutosaveProtocol, *args, **kwargs) -> None:
        if self._autosave_on_change and self._autosave_enabled:
            self.disable_autosave()

        func(self, *args, **kwargs)

        if self._autosave_on_change and not self._autosave_enabled:
            self.enable_autosave()

    return cast(T, wrapper)
