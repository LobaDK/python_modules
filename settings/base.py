from __future__ import annotations
from logging import Logger
from typing import (
    Dict,
    Optional,
    Any,
    IO,
    Callable,
    List,
    Tuple,
    TypeVar,
    Generic,
)
from pathlib import Path
from json import load, dump
from configparser import ConfigParser
from atexit import register
from platform import system, version, architecture, python_version
from copy import deepcopy

from .exceptions import (
    InvalidPathError,
    UnsupportedFormatError,
    MissingDependencyError,
    SanitizationError,
    SaveError,
    LoadError,
    IniFormatError,
)
from .decorators import toggle_autosave_off
from .subclasses import DotDict


T = TypeVar("T")

# Initialize flags indicating the availability of optional modules
yaml_available = False
toml_available = False
logging_available = False

# Attempt to import optional modules and set flags accordingly
try:
    from yaml import safe_load, safe_dump

    yaml_available = True
except ImportError:
    pass

try:
    from toml import load as toml_load, dump as toml_dump

    toml_available = True
except ImportError:
    pass


SUPPORTED_FORMATS: list[str] = ["json", "yaml", "toml", "ini"]


class SettingsManagerBase(DotDict, Generic[T]):
    def __init__(
        self,
        path: Optional[str] = None,
        autosave: bool = False,
        auto_sanitize: bool = False,
        config_format: Optional[str] = None,
        logger: Optional[Logger] = None,
        *,
        default_settings: object,
        read_path: Optional[str] = None,
        write_path: Optional[str] = None,
        autosave_on_exit: bool = False,
        autosave_on_change: bool = False,
        auto_sanitize_on_load: bool = False,
        auto_sanitize_on_save: bool = False,
    ) -> None:
        if not path and not (read_path or write_path):
            raise InvalidPathError(
                "You must provide a path or read_path and write_path."
            )
        if path and (read_path or write_path):
            raise InvalidPathError(
                "You must provide a path or read_path and write_path, not both."
            )

        self.logger: Optional[Logger] = logger

        if self.logger:
            self.logger.info(
                msg=f"\n========== Initializing SettingsManager ==========\nSystem info: {system()} {version()} {architecture()[0]} Python {python_version()}\n"
            )

        if path:
            self._read_path = Path(path)
            self._write_path = Path(path)
        elif read_path and write_path:
            self._read_path = Path(read_path)
            self._write_path = Path(write_path)

        if autosave:
            autosave_on_exit = True
            autosave_on_change = True

        if auto_sanitize:
            auto_sanitize_on_load = True
            auto_sanitize_on_save = True

        if self.logger:
            self.logger.info(
                msg=f"Read path: {self._read_path}. Write path: {self._write_path}."
            )

        if config_format:
            if self.logger:
                self.logger.info(msg=f"User specified format: {config_format}.")
            self._format: str = config_format
        else:
            self._format = self._get_format()
            if self.logger:
                self.logger.info(
                    msg=f"Automatically determined format: {self._format}."
                )

        if self._format not in SUPPORTED_FORMATS:
            if self.logger:
                self.logger.error(
                    msg=f"Format {self._format} is not in the list of supported formats: {', '.join(SUPPORTED_FORMATS)}."
                )
            raise UnsupportedFormatError(
                f"Format {self._format} is not in the list of supported formats: {', '.join(SUPPORTED_FORMATS)}."
            )

        if self._format == "yaml" and not yaml_available:
            if self.logger:
                self.logger.error(msg="The yaml module is not available.")
            raise MissingDependencyError("The yaml module is not available.")

        if self._format == "toml" and not toml_available:
            if self.logger:
                self.logger.error(msg="The toml module is not available.")
            raise MissingDependencyError("The toml module is not available.")

        if autosave_on_exit:
            if self.logger:
                self.logger.info(
                    msg="autosave_on_exit is enabled; registering save method."
                )
            register(self.save)

        self._first_time_load()

        self._autosave_on_change: bool = autosave_on_change
        self._auto_sanitize_on_load: bool = auto_sanitize_on_load
        self._auto_sanitize_on_save: bool = auto_sanitize_on_save
        self._default_settings: object = default_settings

        if self.logger:
            self.logger.info(msg=f"Auto save on changes? {self._autosave_on_change}.")
            self.logger.info(
                msg=f"Sanitize settings on load? {self._auto_sanitize_on_load}."
            )
            self.logger.info(
                msg=f"Sanitize settings on save? {self._auto_sanitize_on_save}."
            )
            self.logger.info(
                msg=f"SettingsManager initialized with format {self._format}!"
            )

    @toggle_autosave_off
    def _first_time_load(self) -> None:
        """
        Loads the settings from the file if it exists, otherwise applies default settings and saves them to the file.
        """
        if self._read_path.exists():
            if self.logger:
                self.logger.info(
                    msg=f"Settings file {self._read_path} exists; loading settings."
                )
            self.load()
        else:
            if self.logger:
                self.logger.info(
                    msg=f"Settings file {self._read_path} does not exist; applying default settings and saving."
                )
            self._store = deepcopy(x=self._default_settings_as_dict)
            self.save()  # Save the default settings to the file

    def save(self) -> None:
        """
        Save the settings data to a file.

        If the auto_sanitize flag is set to True, the settings will be sanitized before saving.

        Raises:
            SaveError: If there is an error while writing the settings to the file.
        """
        if self._auto_sanitize:
            self.sanitize_settings()
        if self._format == "ini" and not self.valid_ini_format(data=self._store):
            if self.logger:
                self.logger.error(
                    msg="The INI format requires top-level keys to be sections, with settings as nested dictionaries. Please ensure your data follows this structure."
                )
            raise IniFormatError(
                "The INI format requires top-level keys to be sections, with settings as nested dictionaries. Please ensure your data follows this structure."
            )
        # Reference assignment instead of deep copy to avoid unnecessary copying, since we're not modifying the data, and the scope is local to this method.
        # We could also entirely avoid this by changing each save method to directly use the internal data, but the flexibility of the current design is nice.
        settings_data: Dict[str, Any] = self._store
        try:
            with open(file=self._write_path, mode="w") as file:
                self._write(data=settings_data, file=file)
        except IOError as e:
            if self.logger:
                self.logger.exception(msg="Error while writing settings to file.")
            raise SaveError("Error while writing settings to file.") from e

    def _write(self, data: Dict[str, Any], file: IO) -> None:
        """
        Dispatches the write operation to the correct method based on the format attribute.

        Args:
            data (Dict[str, Any]): The settings data to write to the file.
            file (IO): The file object to write the settings to.

        Raises:
            UnsupportedFormatError: If the format is not in the list of supported formats.
        """
        format_to_function: Dict[str, Callable[[Dict[str, Any], IO], None]] = {
            "json": self._write_as_json,
            "yaml": self._write_as_yaml,
            "toml": self._write_as_toml,
            "ini": self._write_as_ini,
        }
        if self._format in format_to_function:
            write_function: Callable[[Dict[str, Any], IO], None] = format_to_function[
                self._format
            ]
            write_function(data, file)
        else:
            if self.logger:
                self.logger.error(
                    msg=f"Format {self._format} is not in the list of supported formats: {', '.join(SUPPORTED_FORMATS)}."
                )
            raise UnsupportedFormatError(
                f"Format {self._format} is not in the list of supported formats: {', '.join(SUPPORTED_FORMATS)}."
            )

    def _write_as_json(self, data: Dict[str, Any], file: IO) -> None:
        dump(obj=data, fp=file, indent=4)

    def _write_as_yaml(self, data: Dict[str, Any], file: IO) -> None:
        safe_dump(data, file)

    def _write_as_toml(self, data: Dict[str, Any], file: IO) -> None:
        toml_dump(data, file)

    def _write_as_ini(self, data: Dict[str, Any], file: IO) -> None:
        config = ConfigParser(allow_no_value=True)
        for section, settings in data.items():
            config[section] = settings
        config.write(fp=file)

    def load(self) -> None:
        """
        Load the settings from the specified file into the internal data attribute. autosave_on_change is not triggered by this method.

        If the auto_sanitize flag is set to True, the settings will be sanitized after reading.

        Raises:
            LoadError: If there is an error while reading the settings from the file.
        """
        try:
            with open(file=self._read_path, mode="r") as f:
                self._store: Dict[str, Any] = self._read(file=f)
                if self._auto_sanitize:
                    self.sanitize_settings()
        except IOError as e:
            if self.logger:
                self.logger.exception(msg="Error while reading settings from file.")
            raise LoadError("Error while reading settings from file.") from e

    def _read(self, file: IO) -> Dict[str, Any]:
        """
        Dispatches the read operation to the correct method based on the format attribute.

        Args:
            file (IO): The file object to read the settings from.

        Returns:
            Dict[str, Any]: The settings data read from the file.

        Raises:
            UnsupportedFormatError: If the format is not in the list of supported formats.
        """
        format_to_function: Dict[str, Callable[[IO], Dict[str, Any]]] = {
            "json": self._read_as_json,
            "yaml": self._read_as_yaml,
            "toml": self._read_as_toml,
            "ini": self._read_as_ini,
        }
        if self._format in format_to_function:
            read_function: Callable[[IO], Dict[str, Any]] = format_to_function[
                self._format
            ]
            return read_function(file)
        else:
            raise UnsupportedFormatError(
                f"Format {self._format} is not in the list of supported formats: {', '.join(SUPPORTED_FORMATS)}."
            )

    def _read_as_json(self, file: IO) -> Dict[str, Any]:
        return load(fp=file)

    def _read_as_yaml(self, file: IO) -> Dict[str, Any]:
        return safe_load(file)

    def _read_as_toml(self, file: IO) -> Dict[str, Any]:
        return toml_load(file)

    def _read_as_ini(self, file: IO) -> Dict[str, Any]:
        config = ConfigParser(allow_no_value=True)
        config.read_file(f=file)
        return {
            section: dict(config.items(section=section))
            for section in config.sections()
        }

    def _get_format(self) -> str:
        """
        Determines the format of the settings file based on the file extension of the read path.

        Returns:
            str: The format of the settings file.

        Raises:
            UnsupportedFormatError: If the file extensions of the read and write paths are different and no format is specified.
            UnsupportedFormatError: If the file extension of the read path is not supported.
        """
        if self._read_path.suffix != self._write_path.suffix:
            raise UnsupportedFormatError(
                "Read and write paths must have the same file extension when not specifying a format."
            )
        extension_to_format: Dict[str, str] = {
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".ini": "ini",
        }
        if self._read_path.suffix in extension_to_format:
            return extension_to_format[self._read_path.suffix]
        else:
            raise UnsupportedFormatError(
                f"Trying to determine format from file extension, got {self._read_path} but only {', '.join(SUPPORTED_FORMATS)} are supported."
            )

    def sanitize_settings(self) -> None:
        """
        Sanitizes the settings data by applying the default settings and removing any invalid or unnecessary values.

        The sanitization process is directly applied to the internal data attribute.

        Raises:
            SanitizationError: If an error occurs while sanitizing the settings.

        """

        try:
            keys_to_remove, keys_to_add = self._sanitize_settings(
                settings=self._store,
                default_settings=self._default_settings_as_dict,
                dict_path="",
            )

            for key in keys_to_remove:
                self._remove_key(key=key)

            for key, value in keys_to_add.items():
                self._add_key(key=key, value=value)
        except SanitizationError as e:
            if self.logger:
                self.logger.exception(msg="Error while sanitizing settings.")
            raise e

    def _sanitize_settings(
        self, settings: Dict[str, Any], default_settings: Dict[str, Any], dict_path: str
    ) -> Tuple[List[str], Dict[str, Any]]:

        keys_to_remove: List[str] = []
        keys_to_add: Dict[str, Any] = {}

        for key in settings:
            current_path: str = f"{dict_path}.{key}" if dict_path else key
            if key not in default_settings:
                keys_to_remove.append(current_path)
            elif isinstance(settings[key], dict) and isinstance(
                default_settings[key], dict
            ):
                nested_keys_to_remove, nested_keys_to_add = self._sanitize_settings(
                    settings=settings[key],
                    default_settings=default_settings[key],
                    dict_path=current_path,
                )
                keys_to_remove.extend(nested_keys_to_remove)
                keys_to_add.update(nested_keys_to_add)
            # Add more conditions here if needed, e.g., for lists of dicts

        for key in default_settings:
            if key not in settings:
                keys_to_add[f"{dict_path}.{key}" if dict_path else key] = (
                    default_settings[key]
                )

        return keys_to_remove, keys_to_add

    def _remove_key(self, key: str) -> None:
        """
        Removes the key from the settings data.

        Args:
            key (str): The key to remove from the settings data.
        """
        keys: List[str] = key.split(sep=".")
        current_dict: Dict[str, Any] = self._store
        for key in keys[:-1]:
            current_dict = current_dict[key]
        del current_dict[keys[-1]]

    def _add_key(self, key: str, value: Any) -> None:
        """
        Adds the key with the specified value to the settings data.

        Args:
            key (str): The key to add to the settings data.
            value (Any): The value to associate with the key.
        """
        keys: List[str] = key.split(sep=".")
        current_dict: Dict[str, Any] = self._store
        for key in keys[:-1]:
            current_dict = current_dict[key]
        current_dict[keys[-1]] = value

    @staticmethod
    def valid_ini_format(data: Dict[str, Any]) -> bool:
        """
        Checks if all top-level keys have nested dictionaries as values.

        Args:
            data (Dict[str, Any]): The settings data to check.

        Returns:
            bool: True if all top-level keys have nested dictionaries as values, False otherwise.
        """
        for _, settings in data.items():
            if not isinstance(settings, dict):
                return False
        return True


settings = SettingsManagerBase(
    path="settings.json",
    autosave=True,
    auto_sanitize=True,
    default_settings={"key": "value"},
)
