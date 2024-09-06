"""
Author: Nicklas H. (LobaDK)
Date: 2024
URL: https://github.com/LobaDK/python_modules

Settings Manager package for handling settings and configuration files in JSON, YAML, TOML, and INI formats.

`base.py`: Contains the base class `SettingsManagerBase` which includes all or the majority of the functionality for handling the settings and configuration files. Subclasses should inherit from this class and implement the abstract methods to provide the necessary functionality for the specific object type they wish to employ.

`settings_manager.py`: Contains two fully implemented and ready-to-use classes, `SettingsManagerWithDataclass` and `SettingsManagerWithClass`, for working with settings created as dataclasses or classes.

Please keep in mind that limitations and restrictions employed by the specific file formats also extend to this package. For example, INI files do not support nested sections, and TOML only supports nesting in the form of tables (dictionaries).

This package is provided "as is" for anyone to use, modify, and distribute, freely and openly. While not required, credit back to the original author is appreciated.

This package is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""

from importlib.util import find_spec
from logging import Logger, getLogger, DEBUG

YAML_INSTALLED: bool = False
TOML_INSTALLED: bool = False


def _is_module_installed(module_name: str) -> bool:
    try:
        return find_spec(name=module_name) is not None
    except ValueError:
        return False


YAML_INSTALLED = _is_module_installed(module_name="yaml")
TOML_INSTALLED = _is_module_installed(module_name="toml")


# No handlers means it uses the LastResort handler, only printing WARNING and above to the sys.stderr.
# If the user sets up their own logger with handlers, this will instead propagate to that logger.
logger: Logger = getLogger(name=__name__)
logger.setLevel(level=DEBUG)
logger.propagate = True
