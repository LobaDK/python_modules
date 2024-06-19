from os import unlink
import unittest

from settings.settings_manager import SettingsManagerAsDict
from settings.settings_manager import create_settings_manager
from settings.exceptions import (
    UnsupportedFormatError,
)


class TestSettingsManager(unittest.TestCase):

    def test_get_format(self):
        # Test that the get_format method returns the correct format
        print(
            "Testing if format is correctly determined and if invalid formats raise an exception..."
        )
        for format in ["json", "yaml", "toml", "ini"]:
            default_settings = {"section": {"key": "value"}}
            settings_manager = create_settings_manager(
                f"settings.{format}", default_settings=default_settings
            )
            self.assertEqual(first=settings_manager._get_format(), second=format)
            unlink(path=f"settings.{format}")
        with self.assertRaises(expected_exception=UnsupportedFormatError):
            create_settings_manager("settings.txt", default_settings={"key": "value"})

    def test_get_settings(self) -> None:
        # Test that we can get the settings from the settings manager like a dictionary
        print("Testing if the correct settings are returned...")
        for format in ["json", "yaml", "toml", "ini"]:
            default_settings: dict[str, dict[str, str]] = {"section": {"key": "value"}}
            settings_path: str = f"settings.{format}"
            settings_manager: SettingsManagerAsDict = create_settings_manager(
                settings_path, default_settings=default_settings
            )
            self.assertEqual(
                first=settings_manager["section"]["key"],
                second=default_settings["section"]["key"],
            )
            unlink(settings_path)

    def test_set_settings(self) -> None:
        # Test that we can set the settings of the settings manager like a dictionary
        print("Testing if the settings are correctly set...")
        for format in ["json", "yaml", "toml", "ini"]:
            default_settings: dict[str, dict[str, str]] = {"section": {"key": "value"}}
            settings_manager: SettingsManagerAsDict = create_settings_manager(
                f"settings.{format}", default_settings=default_settings
            )
            new_settings: dict[str, dict[str, str]] = {"section": {"key": "new_value"}}
            settings_manager["section"]["key"] = new_settings["section"]["key"]
            self.assertEqual(
                first=settings_manager["section"]["key"], second="new_value"
            )
            unlink(path=f"settings.{format}")

    def test_delete_settings(self) -> None:
        # Test that we can delete settings from the settings manager like a dictionary
        print("Testing if the settings are correctly deleted...")
        for format in ["json", "yaml", "toml", "ini"]:
            default_settings: dict[str, dict[str, str]] = {"section": {"key": "value"}}
            settings_manager: SettingsManagerAsDict = create_settings_manager(
                f"settings.{format}", default_settings=default_settings
            )
            del settings_manager["section"]["key"]
            self.assertNotIn(member="key", container=settings_manager["section"])
            unlink(path=f"settings.{format}")


if __name__ == "__main__":
    unittest.main()
