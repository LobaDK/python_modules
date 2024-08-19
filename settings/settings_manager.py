from __future__ import annotations
from json import dumps, loads
from dacite import from_dict
from dataclasses import asdict
from typing import Any, Dict, TypeVar, TYPE_CHECKING, Union


from settings.base import SettingsManagerBase

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

T = TypeVar("T")


class TemplateSettings:
    """
    Used by SettingsManagerClass to convert a dictionary to an object using json.loads and json.dumps.
    """

    def __init__(self, dict: dict) -> None:
        self.__dict__.update(dict)


class SettingsManagerWithDataclass(SettingsManagerBase[T]):
    """
    SettingsManager variant which uses a dataclass to store settings.

    This class provides functionality for managing settings data, including loading, saving, and sanitizing settings.
    Supports type parameterization to help IDEs and type checkers infer which settings object is being used and how it can be used.
    Refer to the Examples section for more information on how to use this class.

    args:
        path (Optional[str]): The path to the settings file. Defaults to None.
        autosave (bool): Flag indicating whether to automatically save the settings after any changes. Defaults to False.
        auto_sanitize (bool): Flag indicating whether to automatically sanitize the settings after loading or saving. Defaults to False.
        config_format (Optional[str]): The format of the settings file. Defaults to None.
        default_settings (T): The default settings data. Must be provided.
        read_path (Optional[str]): The path to read the settings file from. Defaults to None.
        write_path (Optional[str]): The path to write the settings file to. Defaults to None.
        autosave_on_exit (bool): Flag indicating whether to automatically save the settings when the program exits. Defaults to False.
        auto_sanitize_on_load (bool): Flag indicating whether to automatically sanitize the settings after loading. Defaults to False.
        auto_sanitize_on_save (bool): Flag indicating whether to automatically sanitize the settings before saving. Defaults to False.
        ValueError: If default_settings is not provided.

    Attributes:
        settings (T): The current settings data.

    Methods:
        save(): Save the settings data to a file.
        autosave(): A context manager that allows you to save the settings data to a file within a context block.
        load(): Load the settings from the specified file into the internal data attribute.
        sanitize_settings(): Sanitizes the settings data by applying the default settings and removing any invalid or unnecessary values.

    Examples:
        ```
        >>> from dataclasses import dataclass, field

        >>> @dataclass
        ... class MySection:
        ...    section_key: str = field(default="section_value")

        >>> @dataclass
        ... class MySettings:
        ...    key: str = field(default="value")
        ...    section: MySection = field(default_factory=MySection)

        >>> settings_manager: SettingsManagerWithDataclass[MySettings] = SettingsManagerWithDataclass(
        ...    path="settings.json",
        ...    default_settings=MySettings()
        ... )

        # The class already automatically loads the settings data from the file, but it can be done manually as well:
        >>> settings_manager.load()

        # Access the settings data directly:
        >>> print(settings_manager.settings.key)
        value

        >>> print(settings_manager.settings.section.section_key)
        section_value

        # Modify the settings data:
        >>> settings_manager.settings.key = "new_value"
        >>> settings_manager.settings.section.section_key = "new_section_value"

        # Save the modified settings data to the file:
        >>> settings_manager.save()

        # Using the autosave context manager, you can mimic the behavior of autosaving after any changes:
        >>> with settings_manager.autosave():
        ...    settings_manager.settings.key = "new_value"
        ...    settings_manager.settings.section.section_key = "new_section_value"

        ```
    """

    def _to_dict(self, obj: "DataclassInstance") -> Dict[str, Any]:
        """
        Converts the settings object to a dictionary using dataclasses.asdict.

        Args:
            obj (object): The settings object to convert to a dictionary.

        Returns:
            Dict[str, Any]: The settings object converted to a dictionary.
        """
        return asdict(obj)

    def _from_dict(self, data: Dict[str, Any]) -> T:
        """
        Converts the dictionary data to a settings object using dacite.from_dict.

        Args:
            data (Dict[str, Any]): The dictionary data to convert to a settings object.

        Returns:
            T: The dictionary data converted to a settings object.
        """
        return from_dict(data_class=self._default_settings.__class__, data=data)


class SettingsManagerWithClass(SettingsManagerBase[T]):
    def _to_dict(self, obj: object) -> Dict[str, Any]:
        """
        Converts the settings object to a dictionary a custom method which iterates through the object's attributes.

        Args:
            obj (object): _description_

        Returns:
            Dict[str, Any]: _description_
        """
        new_dict = self._class_to_dict(obj=obj)
        if not isinstance(new_dict, dict):
            raise TypeError("Settings object must be a dictionary.")
        return new_dict

    def _from_dict(self, data: Dict[str, Any]) -> T:
        """
        Converts the dictionary data to a settings object using json.loads and json.dumps.

        Args:
            data (Dict[str, Any]): The dictionary data to convert to a settings object.

        Returns:
            T: The dictionary data converted to a settings object.
        """
        return loads(s=dumps(obj=data), object_hook=TemplateSettings)

    def _class_to_dict(self, obj: object) -> Union[dict, list, Dict[str, Any], object]:
        """
        Recursively converts a given object to a dictionary representation.

        Args:
            obj (object): The object to be converted.

        Returns:
            dict | list | dict[str, Any] | object: The dictionary representation of the object.

        """
        if isinstance(obj, dict):
            return {key: self._class_to_dict(obj=obj) for key, obj in obj.items()}
        elif isinstance(obj, list):
            return [self._class_to_dict(obj=obj) for obj in obj]
        elif hasattr(obj, "__dict__"):
            return {
                key: self._class_to_dict(obj=value) for key, value in vars(obj).items()
            }
        else:
            return obj
