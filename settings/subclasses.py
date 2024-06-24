from collections import UserDict
from collections.abc import Iterator
from typing import Any, Callable, Iterable, SupportsIndex, Union, overload
from copy import deepcopy


class ChangeDetectingDict(UserDict):
    def __init__(self, state_change_callable: Callable[[Any], None]) -> None:
        # This should not actually be used, but exists to satisfy IDE's and type checkers. The actual store is the _store property in SettingsManagerBase.
        self._store: ChangeDetectingDict
        self._state_change_callable: Callable[[Any], None] = state_change_callable

    def __getitem__(self, key: Any) -> Any:
        return self._store[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self._store[key] = self._wrap(value=value)
        self._state_change_callable(deepcopy(self._store))

    def __delitem__(self, key: Any) -> None:
        del self._store[key]
        self._state_change_callable(deepcopy(self._store))

    def __iter__(self) -> Iterator:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def _wrap(self, value: Any) -> Any:
        # Rebuild and wrap the value if it is a dictionary or list, including nested dictionaries and lists
        if isinstance(value, dict):
            return ChangeDetectingDict(
                state_change_callable=self._state_change_callable,
            )
        elif isinstance(value, list):
            return ChangeDetectingList(
                state_change_callable=self._state_change_callable,
            )
        return value


class ChangeDetectingList(list):
    def __init__(self, state_change_callable: Callable[[Any], None]) -> None:
        self.store: ChangeDetectingList
        self._state_change_callable: Callable[[Any], None] = state_change_callable

    def append(self, value: Any) -> None:
        self.store.append(self._wrap(value=value))
        self._state_change_callable(deepcopy(self.store))

    def extend(self, values: Iterable[Any]) -> None:
        self.store.extend(self._wrap(value=value) for value in values)
        self._state_change_callable(deepcopy(self.store))

    def insert(self, index: SupportsIndex, value: Any) -> None:
        self.store.insert(index, self._wrap(value=value))
        self._state_change_callable(deepcopy(self.store))

    # fmt: off
    @overload
    def __setitem__(self, index: SupportsIndex, value: Any) -> None:
        ...
    # fmt: on

    # fmt: off
    @overload
    def __setitem__(self, index: slice, value: Iterable[Any]) -> None:
        ...
    # fmt: on

    def __setitem__(
        self, index: Union[SupportsIndex, slice], value: Union[Any, Iterable[Any]]
    ) -> None:
        self.store[index] = self._wrap(value=value)
        self._state_change_callable(deepcopy(self.store))

    def __delitem__(self, index: Union[SupportsIndex, slice]) -> None:
        self.store.__delitem__(index)
        self._state_change_callable(deepcopy(self.store))

    def _wrap(self, value: Any) -> Any:
        if isinstance(value, dict):
            return ChangeDetectingDict(
                state_change_callable=self._state_change_callable,
            )
        elif isinstance(value, list):
            return ChangeDetectingList(
                state_change_callable=self._state_change_callable,
            )
        return value
