from os import unlink
from pathlib import Path
from dataclasses import dataclass, field
from subprocess import run
import logging
import unittest

from log_helper.log_helper import LogHelper
from settings.settings_manager import (
    SettingsManagerWithDataclass,
    SettingsManagerWithClass,
)
from settings.exceptions import UnsupportedFormatError


logger: logging.Logger = LogHelper.create_logger(
    logger_name="settings",
    log_file="./tests.log",
    file_log_level=logging.DEBUG,
    stream_log_level=logging.ERROR,
    ignore_existing=True,
)

formats: list[str] = ["json", "yaml", "toml", "ini"]


@dataclass
class DataclassSection:
    key: str = field(default="value")


@dataclass
class DefaultSettingsAsDataClass:
    section: DataclassSection = field(default_factory=DataclassSection)


class ClassSection:
    def __init__(self) -> None:
        self.key: str = "value"


class DefaultSettingsAsClass:
    def __init__(self) -> None:
        self.section: ClassSection = ClassSection()


default_settings_as_Dataclass = DefaultSettingsAsDataClass()
default_settings_as_Class = DefaultSettingsAsClass()


class TestSettingsManager(unittest.TestCase):
    @classmethod
    def tearDownClass(cls) -> None:
        if Path("settings.json").exists():
            unlink(path="settings.json")
        if Path("settings.yaml").exists():
            unlink(path="settings.yaml")
        if Path("settings.toml").exists():
            unlink(path="settings.toml")
        if Path("settings.ini").exists():
            unlink(path="settings.ini")

    def test_get_format(self) -> None:

        # Test that the get_format method returns the correct format
        settings_manager = SettingsManagerWithDataclass(
            path="settings.json",
            default_settings=default_settings_as_Dataclass,
        )
        self.assertEqual(first=settings_manager._format, second="json")
        unlink(path="settings.json")

        with self.assertRaises(expected_exception=UnsupportedFormatError):
            SettingsManagerWithDataclass(
                path="settings.txt", default_settings={"key": "value"}
            )

    def test_get_settings(self) -> None:
        # Test that we can get the settings from the settings manager like a dictionary
        settings_path: str = "settings.json"
        settings_manager = SettingsManagerWithDataclass(
            path=settings_path, default_settings=default_settings_as_Dataclass
        )
        self.assertEqual(
            first=settings_manager.settings.section.key,
            second=default_settings_as_Dataclass.section.key,
        )
        unlink(path=settings_path)

    def test_save_and_load_settings(self) -> None:
        # Test that we can save the settings to a file
        settings_manager = SettingsManagerWithDataclass(
            path="settings.json",
            default_settings=default_settings_as_Dataclass,
        )
        settings_manager.settings.section.key = "new_value"
        settings_manager.save()
        settings_manager = SettingsManagerWithDataclass(
            path="settings.json",
            default_settings=default_settings_as_Dataclass,
        )
        self.assertEqual(
            first=settings_manager.settings.section.key, second="new_value"
        )
        unlink(path="settings.json")

    def test_all_parameters(self) -> None:
        # Test that we can set all the parameters of the settings manager
        settings_manager = SettingsManagerWithDataclass(
            path="settings.json",
            default_settings=default_settings_as_Dataclass,
            autosave=True,
            auto_sanitize=True,
            config_format="json",
        )
        self.assertEqual(first=settings_manager.settings.section.key, second="value")
        unlink(path="settings.json")

    def test_sanitize_settings(self) -> None:
        # Test that we can sanitize the settings
        settings_manager = SettingsManagerWithClass(
            path="settings.json",
            default_settings=default_settings_as_Class,
            auto_sanitize=True,
        )
        settings_manager.settings.section.new_key = "new_value"  # type: ignore[attr-defined] # Linters will properly complain about the attribute not existing
        settings_manager.save()
        settings_manager = SettingsManagerWithClass(
            path="settings.json",
            default_settings=default_settings_as_Class,
            auto_sanitize=True,
        )
        self.assertFalse(expr=hasattr(settings_manager.settings.section, "new_key"))
        unlink(path="settings.json")

    def test_auto_save_on_exit(self) -> None:
        # Test that the settings are saved on exit when autosave is set to True

        # Creates an instance of the settings manager, path as settings.json and autosave set to True.
        # The section.key setting is changed to "new value" and then the subscript exits.
        run(args=["python", "tests/autosave_subscript_test.py"])

        settings_manager = SettingsManagerWithDataclass(
            path="settings.json", default_settings=default_settings_as_Dataclass
        )
        self.assertEqual(
            first=settings_manager.settings.section.key, second="new value"
        )
        unlink(path="settings.json")

    def test_save_context_manager(self) -> None:
        # Test that the settings are saved when using the context manager
        settings_manager = SettingsManagerWithDataclass(
            path="settings.json", default_settings=default_settings_as_Dataclass
        )

        with settings_manager.save_context():
            settings_manager.settings.section.key = "new value"

        self.assertEqual(
            first=settings_manager.settings.section.key, second="new value"
        )
        unlink(path="settings.json")


if __name__ == "__main__":
    unittest.main()
