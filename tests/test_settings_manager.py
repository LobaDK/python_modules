from os import unlink
from subprocess import run
from typing import Dict, Union, List, Tuple
from unittest.mock import patch, mock_open
import logging
import unittest

from log_helper.log_helper import LogHelper
from settings.settings_manager import (
    SettingsManagerWithDataclass,
    SettingsManagerWithClass,
)
from settings.exceptions import UnsupportedFormatError, LoadError, SaveError
from tests.classes.settings_classes import (
    DefaultSettingsAsDataClass,
    DefaultINIFileSettingsAsDataClass,
    DefaultTOMLFileSettingsAsDataClass,
    DefaultSettingsAsClass,
    DefaultINIFileSettingsAsClass,
    DefaultTOMLFileSettingsAsClass,
)


logger: logging.Logger = LogHelper.create_logger(
    logger_name="settings",
    log_file="./tests.log",
    file_log_level=logging.DEBUG,
    stream_log_level=logging.CRITICAL,
    ignore_existing=True,
)

default_settings_as_Dataclass = DefaultSettingsAsDataClass()
default_TOML_settings_as_Dataclass = DefaultTOMLFileSettingsAsDataClass()
default_INI_settings_as_Dataclass = DefaultINIFileSettingsAsDataClass()

default_settings_as_Class = DefaultSettingsAsClass()
default_TOML_settings_as_Class = DefaultTOMLFileSettingsAsClass()
default_INI_settings_as_Class = DefaultINIFileSettingsAsClass()


formats: Dict[
    str,
    List[
        Tuple[
            Union[
                DefaultSettingsAsDataClass,
                DefaultTOMLFileSettingsAsDataClass,
                DefaultINIFileSettingsAsDataClass,
                DefaultSettingsAsClass,
                DefaultTOMLFileSettingsAsClass,
                DefaultINIFileSettingsAsClass,
            ],
            Union[SettingsManagerWithDataclass, SettingsManagerWithClass],
        ]
    ],
] = {
    "json": [
        (default_settings_as_Dataclass, SettingsManagerWithDataclass),
        (default_settings_as_Class, SettingsManagerWithClass),
    ],
    "yaml": [
        (default_settings_as_Dataclass, SettingsManagerWithDataclass),
        (default_settings_as_Class, SettingsManagerWithClass),
    ],
    "toml": [
        (default_TOML_settings_as_Dataclass, SettingsManagerWithDataclass),
        (default_TOML_settings_as_Class, SettingsManagerWithClass),
    ],
    "ini": [
        (default_INI_settings_as_Dataclass, SettingsManagerWithDataclass),
        (default_INI_settings_as_Class, SettingsManagerWithClass),
    ],
}


class TestSettingsManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for format in formats:
            try:
                unlink(path=f"settings.{format}")
            except FileNotFoundError:
                pass

    def test_os_error_on_load_and_save(self) -> None:
        for format in formats:
            for settings_class, manager in formats[format]:
                with self.subTest(format=format, settings_class=settings_class):
                    settings_manager: Union[
                        SettingsManagerWithDataclass, SettingsManagerWithClass
                    ] = manager(
                        path=f"settings.{format}", default_settings=settings_class
                    )
                    with patch("builtins.open", mock_open()) as mocked_open:
                        mocked_open.side_effect = OSError
                        with self.assertRaises(expected_exception=LoadError):
                            settings_manager.load()

                        with self.assertRaises(expected_exception=SaveError):
                            settings_manager.save()

                unlink(path=f"settings.{format}")

    def test_get_format(self) -> None:
        for format in formats:
            for settings_class, manager in formats[format]:
                with self.subTest(format=format, settings_class=settings_class):
                    settings_manager: Union[
                        SettingsManagerWithDataclass, SettingsManagerWithClass
                    ] = manager(
                        path=f"settings.{format}", default_settings=settings_class
                    )
                    self.assertEqual(first=settings_manager._format, second=format)
                unlink(path=f"settings.{format}")

        with self.assertRaises(expected_exception=UnsupportedFormatError):
            SettingsManagerWithDataclass(
                path="settings.txt", default_settings=default_settings_as_Dataclass
            )

    def test_get_all_dataclass_settings(self) -> None:
        for format in formats:
            for settings_class, manager in formats[format]:
                with self.subTest(format=format, settings_class=settings_class):
                    if isinstance(settings_class, DefaultSettingsAsDataClass):
                        settings_manager: SettingsManagerWithDataclass = manager(
                            path=f"settings.{format}", default_settings=settings_class
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.string_key,
                            second=settings_class.section.string_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.int_key,
                            second=settings_class.section.int_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.float_key,
                            second=settings_class.section.float_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.bool_key,
                            second=settings_class.section.bool_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.list_key[0],
                            second=settings_class.section.list_key[0],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.list_key[1]["key1"],
                            second=settings_class.section.list_key[1]["key1"],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key["key1"],
                            second=settings_class.section.dict_key["key1"],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key["key2"],
                            second=settings_class.section.dict_key["key2"],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.nested_section.string_key_in_sub_section,
                            second=settings_class.section.nested_section.string_key_in_sub_section,
                        )
                    elif isinstance(settings_class, DefaultTOMLFileSettingsAsDataClass):
                        settings_manager: SettingsManagerWithDataclass = manager(
                            path=f"settings.{format}", default_settings=settings_class
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.string_key,
                            second=settings_class.section.string_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.int_key,
                            second=settings_class.section.int_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.float_key,
                            second=settings_class.section.float_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.bool_key,
                            second=settings_class.section.bool_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key["key1"],
                            second=settings_class.section.dict_key["key1"],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key["key2"],
                            second=settings_class.section.dict_key["key2"],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.nested_section.string_key_in_sub_section,
                            second=settings_class.section.nested_section.string_key_in_sub_section,
                        )
                    elif isinstance(settings_class, DefaultINIFileSettingsAsDataClass):
                        settings_manager: SettingsManagerWithDataclass = manager(
                            path=f"settings.{format}", default_settings=settings_class
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.string_key,
                            second=settings_class.section.string_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.int_key,
                            second=settings_class.section.int_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.float_key,
                            second=settings_class.section.float_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.bool_key,
                            second=settings_class.section.bool_key,
                        )
            unlink(path=f"settings.{format}")

    def test_get_all_class_settings(self) -> None:
        for format in formats:
            for settings_class, manager in formats[format]:
                with self.subTest(format=format, settings_class=settings_class):
                    if isinstance(settings_class, DefaultSettingsAsClass):
                        settings_manager: SettingsManagerWithClass = manager(
                            path=f"settings.{format}", default_settings=settings_class
                        )

                        self.assertEqual(
                            first=settings_manager.settings.section.string_key,
                            second=default_settings_as_Class.section.string_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.int_key,
                            second=default_settings_as_Class.section.int_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.float_key,
                            second=default_settings_as_Class.section.float_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.bool_key,
                            second=default_settings_as_Class.section.bool_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.list_key[0],
                            second=default_settings_as_Class.section.list_key[0],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.list_key[
                                1
                            ].string_key_in_sub_section,
                            second=default_settings_as_Class.section.list_key[
                                1
                            ].string_key_in_sub_section,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key["key1"],
                            second=default_settings_as_Class.section.dict_key["key1"],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key[
                                "key2"
                            ].string_key_in_sub_section,
                            second=default_settings_as_Class.section.dict_key[
                                "key2"
                            ].string_key_in_sub_section,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.nested_section.string_key_in_sub_section,
                            second=default_settings_as_Class.section.nested_section.string_key_in_sub_section,
                        )
                    elif isinstance(settings_class, DefaultTOMLFileSettingsAsClass):
                        settings_manager: SettingsManagerWithClass = manager(
                            path=f"settings.{format}", default_settings=settings_class
                        )

                        self.assertEqual(
                            first=settings_manager.settings.section.string_key,
                            second=default_TOML_settings_as_Class.section.string_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.int_key,
                            second=default_TOML_settings_as_Class.section.int_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.float_key,
                            second=default_TOML_settings_as_Class.section.float_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.bool_key,
                            second=default_TOML_settings_as_Class.section.bool_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key["key1"],
                            second=default_TOML_settings_as_Class.section.dict_key[
                                "key1"
                            ],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.dict_key["key2"],
                            second=default_TOML_settings_as_Class.section.dict_key[
                                "key2"
                            ],
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.nested_section.string_key_in_sub_section,
                            second=default_TOML_settings_as_Class.section.nested_section.string_key_in_sub_section,
                        )
                    elif isinstance(settings_class, DefaultINIFileSettingsAsClass):
                        settings_manager: SettingsManagerWithClass = manager(
                            path=f"settings.{format}", default_settings=settings_class
                        )

                        self.assertEqual(
                            first=settings_manager.settings.section.string_key,
                            second=default_INI_settings_as_Class.section.string_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.int_key,
                            second=default_INI_settings_as_Class.section.int_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.float_key,
                            second=default_INI_settings_as_Class.section.float_key,
                        )
                        self.assertEqual(
                            first=settings_manager.settings.section.bool_key,
                            second=default_INI_settings_as_Class.section.bool_key,
                        )
            unlink(path=f"settings.{format}")

    def test_save_and_load_settings(self) -> None:
        for format in formats:
            for settings_class, manager in formats[format]:
                with self.subTest(format=format, settings_class=settings_class):
                    settings_manager: Union[
                        SettingsManagerWithDataclass, SettingsManagerWithClass
                    ] = manager(
                        path=f"settings.{format}", default_settings=settings_class
                    )
                    settings_manager.settings.section.string_key = "new_value"
                    settings_manager.save()
                    settings_manager = manager(
                        path=f"settings.{format}", default_settings=settings_class
                    )
                    self.assertEqual(
                        first=settings_manager.settings.section.string_key,
                        second="new_value",
                    )
                unlink(path=f"settings.{format}")

    def test_sanitize_settings(self) -> None:
        for format in formats:
            for settings_class, manager in formats[format]:
                with self.subTest(format=format, settings_class=settings_class):
                    settings_manager: Union[
                        SettingsManagerWithDataclass, SettingsManagerWithClass
                    ] = manager(
                        path=f"settings.{format}",
                        default_settings=settings_class,
                        auto_sanitize=True,
                    )

                    setattr(settings_manager.settings.section, "new_key", "new_value")
                    settings_manager.save()

                    settings_manager = manager(
                        path=f"settings.{format}", default_settings=settings_class
                    )
                    self.assertFalse(
                        hasattr(settings_manager.settings.section, "new_key")
                    )

                    unlink(path=f"settings.{format}")

    def test_auto_save_on_exit(self) -> None:
        # Test that the settings are saved on exit when autosave is set to True

        # Creates an instance of the settings manager, path as settings.json and autosave set to True.
        # The section.key setting is changed to "new value" and then the subscript exits.
        run(args=["python", "tests/autosave_subscript_test.py"])

        settings_manager = SettingsManagerWithDataclass(
            path="settings.json", default_settings=default_settings_as_Dataclass
        )
        self.assertEqual(
            first=settings_manager.settings.section.string_key, second="new value"
        )
        unlink(path="settings.json")

    def test_save_context_manager(self) -> None:
        # Test that the settings are saved when using the context manager
        for format in formats:
            for settings_class, manager in formats[format]:
                with self.subTest(format=format, settings_class=settings_class):
                    settings_manager: Union[
                        SettingsManagerWithDataclass, SettingsManagerWithClass
                    ] = manager(
                        path=f"settings.{format}", default_settings=settings_class
                    )

                    with settings_manager.autosave():
                        settings_manager.settings.section.string_key = "new value"

                    settings_manager = manager(
                        path=f"settings.{format}", default_settings=settings_class
                    )
                    self.assertEqual(
                        first=settings_manager.settings.section.string_key,
                        second="new value",
                    )
                unlink(path=f"settings.{format}")


if __name__ == "__main__":
    unittest.main()
