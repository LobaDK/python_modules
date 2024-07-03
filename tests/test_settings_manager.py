from logging import Logger
from os import unlink
from pathlib import Path
from dataclasses import dataclass, field
import unittest

from log_helper.log_helper import LogHelper
from settings.settings_manager import SettingsManagerAsDict, SettingsManagerAsDataclass
from settings.exceptions import (
    UnsupportedFormatError,
)

logger: Logger = LogHelper.create_logger(logger_name=__name__, log_file="./tests.log")

default_settings_as_dict: dict[str, dict[str, str]] = {"section": {"key": "value"}}


formats: list[str] = ["json", "yaml", "toml", "ini"]


@dataclass
class Section:
    key: str = field(default="value")


@dataclass
class DefaultSettingsAsDataclass:

    section: Section = field(default_factory=Section)


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
        print(
            "Testing if format is correctly determined and if invalid formats raise an exception..."
        )
        for format in formats:
            settings_manager = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
            )
            self.assertEqual(first=settings_manager._get_format(), second=format)
            unlink(path=f"settings.{format}")
        with self.assertRaises(expected_exception=UnsupportedFormatError):
            SettingsManagerAsDict("settings.txt", default_settings={"key": "value"})

    def test_get_settings(self) -> None:
        # Test that we can get the settings from the settings manager like a dictionary
        print("Testing if the correct settings are returned...")
        for format in formats:
            settings_path: str = f"settings.{format}"
            settings_manager: SettingsManagerAsDict = SettingsManagerAsDict(
                settings_path, default_settings=default_settings_as_dict, logger=logger
            )
            self.assertEqual(
                first=settings_manager["section"]["key"],
                second=default_settings_as_dict["section"]["key"],
            )
            unlink(settings_path)

    def test_set_settings(self) -> None:
        # Test that we can set the settings of the settings manager like a dictionary
        print("Testing if the settings are correctly set...")
        for format in formats:
            settings_manager: SettingsManagerAsDict = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
            )
            settings_manager["section"]["new_key"] = "new_value"
            self.assertEqual(
                first=settings_manager["section"]["new_key"], second="new_value"
            )
            unlink(path=f"settings.{format}")

    def test_delete_settings(self) -> None:
        # Test that we can delete settings from the settings manager like a dictionary
        print("Testing if the settings are correctly deleted...")
        for format in formats:
            settings_manager: SettingsManagerAsDict = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
            )
            del settings_manager["section"]["key"]
            self.assertNotIn(member="key", container=settings_manager["section"])
            unlink(path=f"settings.{format}")

    def test_save_and_load_settings(self) -> None:
        # Test that we can save the settings to a file
        print("Testing if the settings are correctly saved and loaded...")
        for format in formats:
            settings_manager: SettingsManagerAsDict = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
            )
            settings_manager.save()
            settings_manager = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
            )
            self.assertEqual(first=settings_manager["section"]["key"], second="value")
            unlink(path=f"settings.{format}")

    def test_all_parameters(self) -> None:
        # Test that we can set all the parameters of the settings manager
        print("Testing if all parameters are correctly set...")
        for format in formats:
            settings_manager: SettingsManagerAsDict = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
                autosave_on_change=True,
                autosave_on_exit=True,
                auto_sanitize=True,
                format=format,
            )
            self.assertEqual(first=settings_manager["section"]["key"], second="value")
            unlink(path=f"settings.{format}")

    def test_sanitize_settings(self) -> None:
        # Test that we can sanitize the settings
        print("Testing if the settings are correctly sanitized...")
        for format in formats:
            settings_manager: SettingsManagerAsDict = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
                auto_sanitize=True,
            )
            settings_manager["section"]["new_key"] = "new_value"
            settings_manager.save()
            settings_manager = SettingsManagerAsDict(
                f"settings.{format}",
                default_settings=default_settings_as_dict,
                logger=logger,
                auto_sanitize=True,
            )
            self.assertNotIn(member="new_key", container=settings_manager["section"])
            unlink(path=f"settings.{format}")

    def test_dataclass(self) -> None:
        # Test that we can use dataclasses as settings
        print("Testing if dataclasses can be used as settings...")
        default_settings: DefaultSettingsAsDataclass = DefaultSettingsAsDataclass()
        for format in formats:
            settings_manager: SettingsManagerAsDataclass[DefaultSettingsAsDataclass] = (
                SettingsManagerAsDataclass(
                    f"settings.{format}",
                    default_settings=default_settings,
                    logger=logger,
                )
            )
            self.assertEqual(
                first=settings_manager.settings.section.key, second="value"
            )
            unlink(path=f"settings.{format}")


if __name__ == "__main__":
    unittest.main()
