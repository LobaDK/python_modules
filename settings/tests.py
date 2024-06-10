from os import path
from os import unlink
import unittest
from unittest.mock import patch
import atexit
from settings_manager import SettingsManager  # type: ignore


class TestSettingsManager(unittest.TestCase):
    def tearDown(self) -> None:
        if path.exists("settings.json"):
            unlink("settings.json")
        if path.exists("settings.yaml"):
            unlink("settings.yaml")
        if path.exists("settings.toml"):
            unlink("settings.toml")
        if path.exists("settings.ini"):
            unlink("settings.ini")

    def test_initialization(self):
        # Test that the SettingsManager object is initialized correctly
        settings_manager = SettingsManager(
            "settings.json",
            default_settings={"key": "value"},
            save_on_exit=True,
            use_logger=True,
            sanitize=True,
            format="json",
        )
        self.assertEqual(settings_manager.default_settings, {"key": "value"})
        self.assertEqual(settings_manager.read_path, "settings.json")
        self.assertEqual(settings_manager.write_path, "settings.json")
        self.assertTrue(settings_manager.save_on_exit)
        self.assertTrue(settings_manager.use_logger)
        self.assertTrue(settings_manager.sanitize)
        self.assertEqual(settings_manager.format, "json")

    def test_get_format(self):
        # Test that the get_format method returns the correct format
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        self.assertEqual(settings_manager._get_format(), "json")

        settings_manager = SettingsManager(
            "settings.yaml", default_settings={"key": "value"}
        )
        self.assertEqual(settings_manager._get_format(), "yaml")

        settings_manager = SettingsManager(
            "settings.toml", default_settings={"key": "value"}
        )
        self.assertEqual(settings_manager._get_format(), "toml")

        settings_manager = SettingsManager(
            "settings.ini", default_settings={"key": "value"}
        )
        self.assertEqual(settings_manager._get_format(), "ini")

    def test_get_format_invalid(self):
        # Test that the get_format method raises a ValueError for an invalid format
        with self.assertRaises(ValueError):
            SettingsManager("settings.txt", default_settings={"key": "value"})

    def test_load_json(self):
        # Test that the _load method loads a JSON file correctly
        with open("settings.json", "w") as f:
            f.write('{"key": "value"}')
        settings_manager = SettingsManager(
            "settings.json", default_settings={"default_key": "default_value"}
        )
        self.assertEqual(settings_manager.data, {"key": "value"})

    def test_load_yaml(self):
        # Test that the _load method loads a YAML file correctly
        with open("settings.yaml", "w") as f:
            f.write("key: value")
        settings_manager = SettingsManager(
            "settings.yaml", default_settings={"default_key": "default_value"}
        )
        self.assertEqual(settings_manager.data, {"key": "value"})

    def test_load_toml(self):
        # Test that the _load method loads a TOML file correctly
        with open("settings.toml", "w") as f:
            f.write('key = "value"')
        settings_manager = SettingsManager(
            "settings.toml", default_settings={"default_key": "default_value"}
        )
        self.assertEqual(settings_manager.data, {"key": "value"})

    def test_load_ini(self):
        # Test that the _load method loads an INI file correctly
        with open("settings.ini", "w") as f:
            f.write("[TEST]\nkey = value")
        settings_manager = SettingsManager(
            "settings.ini", default_settings={"default_key": "default_value"}
        )
        self.assertEqual(settings_manager.data, {"TEST": {"key": "value"}})

    def test_save_json(self):
        # Test that the save method saves a JSON file correctly
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        settings_manager.save()
        with open("settings.json", "r") as f:
            self.assertEqual(f.read(), '{\n    "key": "new_value"\n}')

    def test_save_yaml(self):
        # Test that the save method saves a YAML file correctly
        settings_manager = SettingsManager(
            "settings.yaml", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        settings_manager.save()
        with open("settings.yaml", "r") as f:
            self.assertEqual(f.read(), "key: new_value\n")

    def test_save_toml(self):
        # Test that the save method saves a TOML file correctly
        settings_manager = SettingsManager(
            "settings.toml", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        settings_manager.save()
        with open("settings.toml", "r") as f:
            self.assertEqual(f.read(), 'key = "new_value"\n')

    def test_save_ini(self):
        # Test that the save method saves an INI file correctly
        settings_manager = SettingsManager(
            "settings.ini", default_settings={"key": "value"}
        )
        settings_manager["TEST"] = {"key": "new_value"}
        settings_manager.save()
        with open("settings.ini", "r") as f:
            self.assertEqual(f.read(), "[TEST]\nkey = new_value\n\n")

    def test_getitem(self):
        # Test that the __getitem__ method returns the correct value
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        self.assertEqual(settings_manager["key"], "new_value")

    def test_setitem(self):
        # Test that the __setitem__ method sets the correct value
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        self.assertEqual(settings_manager["key"], "new_value")

    def test_delitem(self):
        # Test that the __delitem__ method deletes the correct value
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        del settings_manager["key"]
        self.assertEqual(settings_manager.data, {})

    def test_iter(self):
        # Test that the __iter__ method returns the correct iterator
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        self.assertEqual(list(iter(settings_manager)), ["key"])

    def test_len(self):
        # Test that the __len__ method returns the correct length
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        self.assertEqual(len(settings_manager), 1)

    @patch.object(SettingsManager, "save")
    def test_save_on_exit(self, mock_save):
        # Create an instance of SettingsManager with save_on_exit enabled
        SettingsManager(
            "settings.json", default_settings={"key": "value"}, save_on_exit=True
        )

        # Manually trigger the atexit handlers to simulate program exit
        atexit._run_exitfuncs()

        # Verify that the save method was called
        mock_save.assert_called_once()

    def test_sanitize_settings(self):
        # Test that the sanitize_settings method removes keys not in default_settings
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["key"] = "new_value"
        settings_manager["extra_key"] = "extra_value"
        settings_manager.sanitize_settings()
        self.assertEqual(settings_manager.data, {"key": "new_value"})

    def test_sanitize_settings_add_missing_keys(self):
        # Test that the sanitize_settings method adds missing keys from default_settings
        settings_manager = SettingsManager(
            "settings.json", default_settings={"key": "value"}
        )
        settings_manager["extra_key"] = "new_value"
        settings_manager.sanitize_settings()
        self.assertEqual(settings_manager.data, {"key": "value"})


if __name__ == "__main__":
    unittest.main()

breakpoint()
