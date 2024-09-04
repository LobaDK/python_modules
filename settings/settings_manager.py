from __future__ import annotations
from dacite import from_dict
from dataclasses import asdict
from typing import Any, Dict, TypeVar, TYPE_CHECKING, Union, Iterable, List, Optional
from inspect import isclass
from json import loads, dumps


from settings import logger
from settings.base import SettingsManagerBase

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

T = TypeVar("T")


class SettingsManagerWithDataclass(SettingsManagerBase[T]):
    """
    SettingsManager variant which uses a dataclass to store settings. Supports saving as JSON, INI, YAML and TOML.

    This class provides functionality for managing settings data, including loading, saving, and sanitizing settings.
    Supports type parameterization to help IDEs and type checkers infer which settings object is being used and its structure.
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
        restore_defaults(): Restores the settings data to the default settings.

    Examples:
        # Import the necessary modules and classes
        >>> from dataclasses import dataclass, field

        # Define the dataclass structure for the settings. This can be as complex as needed. If the format is INI, the dataclass must start with dict-like sections.
        >>> @dataclass
        ... class Section:
        ...    key: str = field(default="value")

        >>> @dataclass
        ... class DefaultSettings:
        ...    section: Section = field(default_factory=Section)

        # Doctest breaks something in the Dacite or typing module if using the defined dataclass, so we must import it as a workaround.
        >>> from tests.test_settings_manager import DefaultSettingsAsDataClass

        # Create an instance of the SettingsManagerWithDataclass class, providing the path to the settings file and the default settings data. The DefaultSettingsAsDataClass class is also provided as the typing parameter, which helps IDEs and type checkers infer the structure of the settings data.
        >>> settings_manager: SettingsManagerWithDataclass[DefaultSettingsAsDataClass] = SettingsManagerWithDataclass(
        ...    path="settings.ini",
        ...    default_settings=DefaultSettingsAsDataClass()
        ... )

        # While the class does automatically load the settings from file if found, it can also be done manually:
        >>> settings_manager.load()

        # Access the settings like any other dataclass instance:
        >>> print(settings_manager.settings.section.key)
        value

        # Modify the settings data:
        >>> settings_manager.settings.section.key = "new_value"

        # Save the settings
        >>> settings_manager.save()

        # Reset the settings to the default values
        >>> settings_manager.restore_defaults()

        # Using the autosave context manager, you can mimic the behavior of autosaving after any changes:
        >>> with settings_manager.autosave():
        ...    settings_manager.settings.section.key = "value"

        # ONLY FOR THE DOCTEST: Clean up the settings file
        >>> from os import unlink
        >>> unlink("settings.ini")

    """

    def _to_dict(self, obj: "DataclassInstance") -> Dict[str, Any]:
        """
        Converts the settings object to a dictionary using dataclasses.asdict.

        Args:
            obj (object): The settings object to convert to a dictionary.

        Returns:
            Dict[str, Any]: The settings object converted to a dictionary.
        """
        logger.debug(msg=f"Converting settings object to dictionary: {obj}")
        return asdict(obj)

    def _from_dict(self, data: Dict[str, Any]) -> T:
        """
        Converts the dictionary data to a settings object using dacite.from_dict.

        Args:
            data (Dict[str, Any]): The dictionary data to convert to a settings object.

        Returns:
            T: The dictionary data converted to a settings object.
        """
        logger.debug(msg=f"Converting data to settings object: {data}")
        return from_dict(data_class=self._default_settings.__class__, data=data)


class SettingsManagerWithClass(SettingsManagerBase[T]):
    """
    SettingsManager variant which uses a standard class to store settings. Supports saving as JSON, INI, YAML and TOML.

    This class provides functionality for managing settings data, including loading, saving, and sanitizing settings.
    Supports type parameterization to help IDEs and type checkers infer which settings object is being used and its structure.
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
        restore_defaults(): Restores the settings data to the default settings.

    Examples:
        # Define the class structure for the settings. This can be as complex as needed. If the format is INI, the class must start with dict-like sections.
        >>> class Section:
        ...     def __init__(self):
        ...         self.section_key = "section_value"

        >>> class Settings:
        ...     def __init__(self):
        ...         self.section = Section()

        # Create an instance of the SettingsManagerWithClass class, providing the path to the settings file and the default settings data. The Settings class is also provided as the typing parameter, which helps IDEs and type checkers infer the structure of the settings data.
        >>> settings_manager: SettingsManagerWithClass[Settings] = SettingsManagerWithClass(
        ...     path="settings.yaml",
        ...     default_settings=Settings()
        ... )

        # While the class does automatically load the settings from file if found, it can also be done manually:
        >>> settings_manager.load()

        # Access the settings like any other class instance:
        >>> print(settings_manager.settings.section.section_key)
        section_value

        # Modify the settings
        >>> settings_manager.settings.section.section_key = "new_section_value"

        # Save the settings
        >>> settings_manager.save()

        # Reset the settings to the default values
        >>> settings_manager.restore_defaults()

        # Using the autosave context manager, you can mimic the behavior of autosaving after any changes:
        >>> with settings_manager.autosave():
        ...     settings_manager.settings.section.section_key = "section_value"

        # ONLY FOR THE DOCTEST: Clean up the settings file
        >>> from os import unlink
        >>> unlink("settings.yaml")

    """

    def _to_dict(self, obj: object) -> Dict[str, Any]:
        """
        Converts the settings object to a dictionary a custom method which iterates through the object's attributes.

        Args:
            obj (object): The settings object to convert to a dictionary.
            include_class_references (bool): Flag indicating whether to include a reference to the class in the dictionary. Operations planning to reconstruct the object from the dictionary should make sure this is set to True. Defaults to True.

        Returns:
            Dict[str, Any]: The settings object converted to a dictionary.
        """
        logger.debug(msg=f"Converting settings object to dictionary: {obj}")
        new_dict = self._class_to_dict(obj=obj)
        if not isinstance(new_dict, dict):
            raise TypeError("Settings object must be a dictionary.")
        return new_dict

    def _from_dict(self, data: Dict[str, Any]) -> T:
        """
        Converts the dictionary data to a settings object using a custom method which iterates through the dictionary.

        Args:
            data (Dict[str, Any]): The dictionary data to convert to a settings object.

        Returns:
            T: The dictionary data converted to a settings object.
        """
        logger.debug(msg=f"Converting data to settings object: {data}")
        return loads(s=dumps(obj=data), object_hook=self._default_settings.__class__)

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
        elif isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
            return [self._class_to_dict(obj=obj) for obj in obj]
        elif hasattr(obj, "__dict__"):
            obj_dict = {
                key: self._class_to_dict(obj=obj) for key, obj in obj.__dict__.items()
            }
            # Add a reference to the class for later reconstruction
            return obj_dict
        else:
            return obj
