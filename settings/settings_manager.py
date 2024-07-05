from __future__ import annotations
from typing import Dict, Optional, Any, TypeVar, TYPE_CHECKING
from dacite import from_dict
from dataclasses import asdict

from .base import SettingsManagerBase


if TYPE_CHECKING:
    from _typeshed import DataclassInstance

T = TypeVar("T", bound="DataclassInstance")


class SettingsManagerAsDict(SettingsManagerBase):
    def _to_dict(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if data:
            return data
        return self._store

    def _from_dict(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if data:
            return data
        return self._store


class SettingsManagerAsDataclass(SettingsManagerBase[T]):
    """
    A class that manages settings using dataclasses.

    This class provides methods to convert settings objects to dictionaries and vice versa.

    Attributes:
        _default_settings: The default settings object.

    Methods:
        _to_dict(data: Any) -> Dict[str, Any]:
            Converts a settings object to a dictionary.

        _from_dict(data: Dict[str, Any]) -> Any:
            Converts a dictionary to a settings object.
    """

    def _to_dict(self, data: Optional[T] = None) -> Dict[str, Any]:
        """
        Converts the given data or the internal data to a dictionary.

        Args:
            data: The data to convert to a dictionary.

        Returns:
            The converted dictionary.
        """
        if data:
            return asdict(obj=data)
        return asdict(obj=self._default_settings)

    def _from_dict(self, data: Optional[Dict[str, Any]] = None) -> T:
        """
        Converts a dictionary representation of data or the internal data to the object it represents.

        Args:
            data: The dictionary containing the data to be converted.

        Returns:
            The converted object.
        """
        if data:
            return from_dict(data_class=self._default_settings.__class__, data=data)
        return from_dict(data_class=self._default_settings.__class__, data=self._store)


class SettingsManagerAsObject(SettingsManagerBase):
    def _to_dict(self, data: Optional[object] = None) -> Dict[str, Any]:
        if data:
            return data.__dict__
        return self._store

    def _from_dict(self, data: Optional[Dict[str, Any]] = None) -> object:
        if data:
            return object.__new__(self._default_settings.__class__, **data)
        return object.__new__(self._default_settings.__class__, **self._store)

    def strip_non_persistent_settings(self, data: object) -> object:
        return self._recursively_strip_non_persistent_settings(obj=data)

    def _recursively_strip_non_persistent_settings(self, obj: object) -> object:
        if not isinstance(obj, (int, float, str, bool, list, tuple, dict)):
            for attr in dir(obj):
                pass
