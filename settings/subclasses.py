from __future__ import annotations
from typing import (
    Any,
    Dict,
    List,
    Set,
    Union,
    SupportsIndex,
    Iterable,
    Tuple,
    Callable,
)


class BaseWrapper:
    def __init__(self, data: Any, callbacks: List[Callable[[], Any]]) -> None:
        self._data: Any = data
        self._callbacks: List[Callable[[], Any]] = callbacks if callbacks else []

    def add_callback(self, callback: Callable[[], Any]) -> None:
        self._callbacks.append(callback)

    def remove_callback(self, callback: Callable[[], Any]) -> None:
        self._callbacks.remove(callback)

    @property
    def callbacks(self) -> List[Callable[[], Any]]:
        return self._callbacks

    @callbacks.setter
    def callbacks(self, value: List[Callable[[], Any]]) -> None:
        self._callbacks = value
        for obj in self._data.values():
            if isinstance(obj, BaseWrapper):
                obj.callbacks = value

    def _notify(self) -> None:
        if self._callbacks:
            for callback in self._callbacks:
                callback()

    def _wrap(self, value: Any) -> Any:
        if isinstance(value, dict):
            return DictWrapper(value, self._callbacks)
        elif isinstance(value, list):
            return ListWrapper(value, self._callbacks)
        elif isinstance(value, set):
            return SetWrapper(value, self._callbacks)
        elif isinstance(value, tuple):
            return TupleWrapper(value, self._callbacks)
        return value


class DictWrapper(BaseWrapper):
    def __getitem__(self, key: Any) -> Any:
        return self._data[key]

    def __setitem__(self, key: Any, value: Any) -> None:
        self._data[key] = self._wrap(value=value)
        self._notify()

    def __delitem__(self, key: Any) -> None:
        del self._data[key]
        self._notify()

    def __getattr__(self, key: Any) -> Any:
        try:
            return self._data[key]
        except KeyError:
            raise AttributeError(
                f"`{self.__class__.__name__}` object has no attribute `{key}`"
            )

    def __setattr__(self, key: str, value: Any) -> None:
        if key in {"_data", "_callbacks"}:
            super().__setattr__(key, value)
        else:
            self._data[key] = self._wrap(value=value)
            self._notify()

    def __delattr__(self, key: str) -> None:
        del self._data[key]
        self._notify()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._data})"

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in self._data.items():
            if isinstance(value, BaseWrapper):
                result[key] = (
                    value.to_dict() if isinstance(value, DictWrapper) else value._data
                )
            else:
                result[key] = value
        return result


class ListWrapper(BaseWrapper, list):
    def __init__(self, data: List[Any], callbacks: List[Callable[[], Any]]) -> None:
        BaseWrapper.__init__(self, data=data, callbacks=callbacks)
        list.__init__(self, (self._wrap(value=value) for value in data))

    def append(self, item: Any) -> None:
        super().append(self._wrap(value=item))
        self._notify()

    def extend(self, items: Iterable[Any]) -> None:
        super().extend(self._wrap(value=item) for item in items)
        self._notify()

    def insert(self, index: SupportsIndex, item: Any) -> None:
        super().insert(index, self._wrap(value=item))
        self._notify()

    def remove(self, item: Any) -> None:
        super().remove(item)
        self._notify()

    def pop(self, index: SupportsIndex = -1) -> Any:
        item = super().pop(index)
        self._notify()
        return item

    def __setitem__(
        self, index: Union[slice, SupportsIndex], value: Union[Iterable[Any], Any]
    ) -> None:
        super().__setitem__(index, self._wrap(value=value))
        self._notify()

    def __delitem__(self, index: Union[SupportsIndex, slice]) -> None:
        super().__delitem__(index)
        self._notify()


class SetWrapper(BaseWrapper, set):
    def __init__(self, data: Set[Any], callbacks: List[Callable[[], Any]]) -> None:
        BaseWrapper.__init__(self, data=data, callbacks=callbacks)
        set.__init__(self, (self._wrap(value=value) for value in data))

    def add(self, item: Any) -> None:
        super().add(self._wrap(value=item))
        self._notify()

    def remove(self, item: Any) -> None:
        super().remove(item)
        self._notify()

    def discard(self, item: Any) -> None:
        super().discard(item)
        self._notify()

    def pop(self) -> Any:
        item = super().pop()
        self._notify()
        return item

    def clear(self) -> None:
        super().clear()
        self._notify()


class TupleWrapper(BaseWrapper, tuple):
    def __new__(
        cls, data: Tuple[Any, ...], callbacks: List[Callable[[], Any]]
    ) -> TupleWrapper:
        obj = super().__new__(
            cls, tuple(cls._wrap(self=cls, value=item) for item in data)
        )
        obj._callbacks = callbacks if callbacks else []
        return obj

    def __init__(
        self, data: Tuple[Any, ...], callbacks: List[Callable[[], Any]] = []
    ) -> None:
        BaseWrapper.__init__(self, data=data, callbacks=callbacks)

    def _replace(self, index: int, value: Any) -> "TupleWrapper":
        new_data = list(self._data)
        new_data[index] = self._wrap(value=value)
        return TupleWrapper(data=tuple(new_data), callbacks=self._callbacks)

    def __setattr__(self, key: str, value: Any) -> None:
        raise AttributeError(f"`{self.__class__.__name__}` object is immutable")

    def __delattr__(self, key: str) -> None:
        raise AttributeError(f"`{self.__class__.__name__}` object is immutable")


class DotDict(DictWrapper):
    """
    A dictionary-like object that supports dot notation for accessing and modifying values.

    DotDict is a subclass of DictWrapper and provides additional functionality for adding and removing callback functions that are called when the data is modified.

    Example usage:
    ```python
    >>> data = DotDict()
    >>> data.key = "value"
    >>> print(data.key)
    value

    ```

    Attributes:
        callbacks (List[Callable[[], Any]]): A list of callback functions to be called when the data is modified.
        _data (Dict[str, Any]): The underlying dictionary that stores the data.

    Methods:
        add_callback(callback: Callable[[], Any]) -> None:
            Adds a callback function to the list of callbacks that should be called when the data is modified.

        remove_callback(callback: Callable[[], Any]) -> None:
            Removes a callback function from the list of callbacks that should be called when the data is modified.

        to_dict() -> Dict[str, Any]:
            Returns a dictionary representation of the DotDict object.
    """

    def __init__(self, *args, **kwargs) -> None:
        initial_data = dict(*args, **kwargs)
        super().__init__(data=initial_data, callbacks=[])

    def add_callback(self, callback: Callable[[], Any]) -> None:
        """
        Adds a callback function to the list of callbacks that should be called when the data is modified.

        Callbacks are called in the order they were added. The callback function should not take any arguments. Any return value is ignored.
        The callbacks list can be accessed and modified directly by accessing the `callbacks` property. Modifications to the callables list will propagate to all nested supported data structures.

        Example usage:
        ```python
        >>> def custom_callback():
        ...    print("Data was modified")
        ...
        >>> data = DotDict()
        >>> data.add_callback(callback=custom_callback)
        ...
        >>> data.key = "value"
        Data was modified

        ```

        Args:
            callback (Callable[[], Any]): The callback function to be added.

        Returns:
            None
        """
        self._callbacks.append(callback)
        for value in self._data.values():
            if isinstance(value, BaseWrapper):
                value.add_callback(callback=callback)

    def remove_callback(self, callback: Callable[[], Any]) -> None:
        """
        Removes a callback function from the list of callbacks that should be called when the data is modified.

        The callback function should be in the list of callbacks. If the callback is not found, ValueError is raised. Modifications to the callables list will propagate to all nested supported data structures.

        Example usage:
        ```python
        >>> def custom_callback():
        ...    print("Data was modified")
        ...
        >>> data = DotDict()
        >>> data.add_callback(callback=custom_callback)
        ...
        >>> data.remove_callback(callback=custom_callback)
        ...
        >>> data.key = "value"

        ```
        Args:
            callback (Callable[[], Any]): The callback function to be removed.

        Returns:
            None
        """
        try:
            self._callbacks.remove(callback)
        except ValueError:
            raise ValueError(f"Callback {callback} not found in list of callbacks.")
        for value in self._data.values():
            if isinstance(value, BaseWrapper):
                value.remove_callback(callback=callback)

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()
