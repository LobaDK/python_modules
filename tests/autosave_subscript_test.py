from dataclasses import dataclass, field
from sys import path as sys_path

sys_path.append(".")

from settings.settings_manager import SettingsManagerWithDataclass


@dataclass
class DataclassSection:
    key: str = field(default="value")


@dataclass
class DefaultSettingsAsDataClass:
    section: DataclassSection = field(default_factory=DataclassSection)


default_settings_as_Dataclass = DefaultSettingsAsDataClass()


settings_manager = SettingsManagerWithDataclass(
    path="settings.json", default_settings=default_settings_as_Dataclass, autosave=True
)

settings_manager.settings.section.key = "new value"
