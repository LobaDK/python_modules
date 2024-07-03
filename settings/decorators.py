from typing import Callable, TypeVar, cast, Protocol
from functools import wraps


class AutosaveProtocol(Protocol):
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
    A decorator that specifically toggles the autosave feature on before calling the decorated function and off after the function is called.

    This is useful for functions that change the settings and autosaving is explicitly desired in the scope of the function call.
    Be aware toggling the autosave feature can be expensive, as each nested `ChangeDetectingDict` and `ChangeDetectingList` gets updated.
    The target function must be an instance method part of a class that implements the following methods:

    - `enable_autosave` to enable the autosave feature
    - `disable_autosave` to disable the autosave feature

    as well as the following attributes:

    - `_autosave_enabled` to keep track of the current state of the autosave feature
    """

    @wraps(wrapped=func)
    def wrapper(self: AutosaveProtocol, *args, **kwargs) -> None:
        if not self._autosave_enabled:
            self.enable_autosave()

        func(self, *args, **kwargs)

        if self._autosave_enabled:
            self.disable_autosave()

    return cast(T, wrapper)


def toggle_autosave_off(func: T) -> T:
    """
    A decorator that specifically toggles the autosave feature off before calling the decorated function and on after the function is called.

    This is useful for functions that change the settings and autosaving is explicitly not desired in the scope of the function call.
    Be aware toggling the autosave feature can be expensive, as each nested `ChangeDetectingDict` and `ChangeDetectingList` gets updated.
    The target function must be an instance method part of a class that implements the following methods:

    - `enable_autosave` to enable the autosave feature
    - `disable_autosave` to disable the autosave feature

    as well as the following attributes:

    - `_autosave_enabled` to keep track of the current state of the autosave feature
    """

    @wraps(wrapped=func)
    def wrapper(self: AutosaveProtocol, *args, **kwargs) -> None:
        if self._autosave_enabled:
            self.disable_autosave()

        func(self, *args, **kwargs)

        if not self._autosave_enabled:
            self.enable_autosave()

    return cast(T, wrapper)
