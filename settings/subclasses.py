from __future__ import annotations
from collections import UserDict
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Union,
    Protocol,
    List,
    SupportsIndex,
)


class ParentProtocol(Protocol):
    # fmt: off
    def save(self) -> None:
        ...
    # fmt: on


class ChangeDetectingDict(UserDict):
    def __init__(
        self,
        parent: Optional[ParentProtocol] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._store: Dict[str, Any] = {}
        self._parent: Optional[ParentProtocol] = parent
        self._autosave_enabled: bool = True
        if data:
            for key, value in data.items():
                self._store[key] = self._wrap(value=value)

    def _wrap(self, value: Any) -> Union[ChangeDetectingDict, ChangeDetectingList, Any]:
        if isinstance(value, dict):
            change_detecting_dict = ChangeDetectingDict(parent=self._parent, data=value)
            change_detecting_dict._set_autosave(state=self._autosave_enabled)
            return change_detecting_dict
        elif isinstance(value, list):
            change_detecting_list = ChangeDetectingList(parent=self._parent, data=value)
            change_detecting_list._set_autosave(state=self._autosave_enabled)
            return change_detecting_list
        return value

    def _set_autosave(self, state: bool) -> None:
        self._autosave_enabled = state
        for key in self._store:
            if isinstance(self._store[key], (ChangeDetectingDict, ChangeDetectingList)):
                self._store[key]._set_autosave(state=state)

    def __getitem__(self, key: str) -> str:
        return self._store[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._store[key] = self._wrap(value=value)
        if self._parent:
            self._parent.save()

    def __delitem__(self, key: str) -> None:
        del self._store[key]
        if self._parent:
            self._parent.save()

    def __iter__(self) -> Iterator[str]:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def enable_autosave(self) -> None:
        self._set_autosave(state=True)

    def disable_autosave(self) -> None:
        self._set_autosave(state=False)


class ChangeDetectingList(list):
    def __init__(
        self, parent: Optional[ParentProtocol] = None, data: Optional[List] = None
    ) -> None:
        self._store: List = []
        self._parent: Optional[ParentProtocol] = parent
        self._autosave_enabled: bool = True
        if data:
            for item in data:
                self._store.append(self._wrap(value=item))

    def _wrap(self, value: Any) -> Union[ChangeDetectingDict, ChangeDetectingList, Any]:
        if isinstance(value, dict):
            change_detecting_dict = ChangeDetectingDict(parent=self._parent, data=value)
            change_detecting_dict._set_autosave(state=self._autosave_enabled)
            return change_detecting_dict
        elif isinstance(value, list):
            change_detecting_list = ChangeDetectingList(parent=self._parent, data=value)
            change_detecting_list._set_autosave(state=self._autosave_enabled)
            return change_detecting_list
        return value

    def _set_autosave(self, state: bool) -> None:
        self._autosave_enabled = state
        for i in range(len(self._store)):
            if isinstance(self._store[i], (ChangeDetectingDict, ChangeDetectingList)):
                self._store[i]._set_autosave(state=state)

    def __getitem__(self, index: Union[int, slice, SupportsIndex]) -> Any:
        return self._store[index]

    def __setitem__(self, index: Union[int, slice, SupportsIndex], value: Any) -> None:
        self._store[index] = self._wrap(value=value)
        if self._parent:
            self._parent.save()

    def __delitem__(self, index: Union[int, slice, SupportsIndex]) -> None:
        del self._store[index]
        if self._parent:
            self._parent.save()

    def insert(self, index: SupportsIndex, value: Any) -> None:
        self._store.insert(index, self._wrap(value=value))
        if self._parent:
            self._parent.save()

    def append(self, object: Any) -> None:
        self._store.append(self._wrap(value=object))
        if self._parent:
            self._parent.save()

    def extend(self, iterable: Iterable) -> None:
        for item in iterable:
            self._store.append(self._wrap(value=item))
        if self._parent:
            self._parent.save()

    def __iter__(self) -> Iterator:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)
