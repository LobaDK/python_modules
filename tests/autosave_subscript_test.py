def main() -> None:
    from dataclasses import dataclass, field
    from typing import Any, Union
    from sys import path as sys_path

    sys_path.append(".")

    from settings.settings_manager import SettingsManagerWithDataclass

    @dataclass
    class DataclassSubSection:
        string_key_in_sub_section: str = field(default="value")

    @dataclass
    class DataclassSection:
        string_key: str = field(default="value")
        list_key: list[Union[str, object]] = field(
            default_factory=lambda: ["value1", DataclassSubSection()]
        )
        dict_key: dict[str, Any] = field(
            default_factory=lambda: {"key1": "value1", "key2": DataclassSubSection()}
        )
        int_key: int = 1
        float_key: float = 1.0
        bool_key: bool = True
        nested_section: DataclassSubSection = field(default_factory=DataclassSubSection)

    @dataclass
    class DefaultSettingsAsDataClass:
        section: DataclassSection = field(default_factory=DataclassSection)

    default_settings_as_Dataclass = DefaultSettingsAsDataClass()

    settings_manager = SettingsManagerWithDataclass(
        path="settings.json",
        default_settings=default_settings_as_Dataclass,
        autosave=True,
    )

    settings_manager.settings.section.string_key = "new value"


if __name__ == "__main__":
    main()
