from typing import Optional
from pathlib import Path
from typing import Dict, overload, Tuple, TypeVar

from settings.exceptions import (
    MissingPathError,
    TooManyPathsError,
    TOMLNotInstalledError,
    YAMLNotInstalledError,
    UnsupportedFormatError,
)
from settings.constants import SUPPORTED_FORMATS
from settings import YAML_INSTALLED, TOML_INSTALLED, logger

T = TypeVar("T", bound=Tuple[bool, ...])


def set_file_paths(
    path: Optional[str] = None,
    read_path: Optional[str] = None,
    write_path: Optional[str] = None,
) -> tuple[Path, Path]:
    """
    Set the file paths for reading and writing.

    Args:
        path (Optional[str]): The path to use for both reading and writing.
        read_path (Optional[str]): The path to use for reading.
        write_path (Optional[str]): The path to use for writing.

    Returns:
        tuple[Path, Path]: A tuple containing the Path objects for the read path and write path.

    Raises:
        MissingPathError: If neither `path` nor `read_path` and `write_path` are provided.
        TooManyPathsError: If both `path` and `read_path` or `write_path` are provided.

    Examples:
        >>> set_file_paths(path="settings.json")  # doctest: +ELLIPSIS
        (...Path('settings.json'), ...Path('settings.json'))
        >>> set_file_paths(read_path="settings.json", write_path="settings.json")  # doctest: +ELLIPSIS
        (...Path('settings.json'), ...Path('settings.json'))

    """
    if not path and not (read_path or write_path):
        raise MissingPathError("You must provide a path or read_path and write_path.")
    if path and (read_path or write_path):
        raise TooManyPathsError(
            "You must provide a path or read_path and write_path, not both."
        )
    if path:
        read_path = path
        write_path = path
    assert read_path is not None and write_path is not None
    return Path(read_path), Path(write_path)


@overload
def set_format(config_format: str) -> str: ...


@overload
def set_format(*, read_path: Path, write_path: Path) -> str: ...


def set_format(
    config_format: Optional[str] = None,
    *,
    read_path: Optional[Path] = None,
    write_path: Optional[Path] = None,
) -> str:
    """
    Sets the format for the configuration.

    Args:
        config_format (str): The desired format for the configuration.
        read_path (Path): The path to the settings file to read.
        write_path (Path): The path to the settings file to write.

    Returns:
        str: The format that was set.

    Raises:
        UnsupportedFormatError: If the specified format is not supported.
        YAMLNotInstalledError: If the YAML format is specified but the PyYAML module is not installed.
        TOMLNotInstalledError: If the TOML format is specified but the TOML module is not installed.

    Examples:
        >>> set_format(config_format="json")
        'json'
        >>> set_format(read_path=Path("settings.json"), write_path=Path("settings.json"))
        'json'

    """
    format: str
    if config_format:
        if logger:
            logger.info(msg=f"User specified format: {config_format}.")
        format = config_format
    elif not config_format and read_path and write_path:
        format = _determine_format_from_file_extension(
            read_path=read_path, write_path=write_path
        )
        if logger:
            logger.info(msg=f"Automatically determined format: {format}.")

    if format not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(
            f"Format {format} is not in the list of supported formats: {', '.join(SUPPORTED_FORMATS)}."
        )

    if format == "yaml" and not YAML_INSTALLED:
        raise YAMLNotInstalledError(
            "The YAML format is not supported because the PyYAML module is not installed."
        )
    if format == "toml" and not TOML_INSTALLED:
        raise TOMLNotInstalledError(
            "The TOML format is not supported because the TOML module is not installed."
        )

    return format


def _determine_format_from_file_extension(
    read_path: Path,
    write_path: Path,
    *,
    extension_to_format: Dict[str, str] = {
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".ini": "ini",
    },  # "Caches" the dictionary to avoid creating it every time the function is called, while adding flexibility.
) -> str:
    """
    Determines the format of the settings file based on the file extension of the read path.

    Args:
        read_path (Path): The path to the settings file to read.
        write_path (Path): The path to the settings file to write.
        extension_to_format (Dict[str, str], optional): A dictionary mapping file extensions to formats. Defaults to {"json": "json", "yaml": "yaml", "yml": "yaml", "toml": "toml", "ini": "ini"}.

    Returns:
        str: The format of the settings file.

    Raises:
        UnsupportedFormatError: If the file extensions of the read and write paths are different or if the file extension is not supported.

    Examples:
        >>> read_path = Path("settings.json")
        >>> write_path = Path("settings.json")
        >>> _determine_format_from_file_extension(read_path, write_path)
        'json'

    """
    read_path_suffix: str = read_path.suffix
    write_path_suffix: str = write_path.suffix
    if read_path_suffix != write_path_suffix:
        raise UnsupportedFormatError(
            "Read and write paths must have the same file extension when not specifying a format."
        )
    if read_path_suffix in extension_to_format:
        return extension_to_format[read_path_suffix]
    else:
        raise UnsupportedFormatError(
            f"Trying to determine format from file extension, got {read_path_suffix} but only {', '.join(SUPPORTED_FORMATS)} are supported."
        )


def composite_toggle(composite: bool, options: T) -> T:
    """
    Uses the composite flag to determine if all individual toggles should be set to True.

    Args:
        composite (bool): The composite flag indicating whether the options should be toggled.
        options (Tuple[bool]): The individual toggles to be updated

    Returns:
        Tuple[bool]: The updated options, excluding the composite flag.

    Raises:
        ValueError: If the composite flag is True and any of the individual toggles are also True.

    Examples:
        >>> composite_toggle(composite=False, options=(True, False, True))
        (True, False, True)
        >>> composite_toggle(composite=True, options=(False, False, False))
        (True, True, True)

    """
    if composite:
        for option in options:
            if option:
                raise ValueError(
                    "The composite flag cannot be True if any of the individual toggles are also True."
                )
        return (True,) * len(options)
    return options


def filter_locals(locals_dict: dict[str, T]) -> dict[str, T]:
    """
    Filters out the private and protected variables from the locals dictionary.

    Args:
        locals_dict (dict[str, T]): The dictionary of local variables.

    Returns:
        dict[str, T]: The filtered dictionary of local variables.

    Examples:
        >>> locals_dict = {"_private": 1, "__protected": 2, "public": 3}
        >>> filter_locals(locals_dict)
        {'public': 3}

    """
    return {key: value for key, value in locals_dict.items() if not key.startswith("_")}