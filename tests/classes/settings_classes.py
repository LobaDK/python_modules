from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


# Dataclass settings for testing JSON and YAML
@dataclass
class DataclassSubSection:
    string_key_in_sub_section: str = field(default="value")


@dataclass
class DataclassSection:
    string_key: str = field(default="value")
    list_key: List[Union[str, Dict[str, Any]]] = field(
        default_factory=lambda: ["value1", {"key1": "value1"}]
    )
    dict_key: Dict[str, Any] = field(
        default_factory=lambda: {"key1": "value1", "key2": "value2"}
    )
    int_key: int = field(default=1)
    float_key: float = field(default=1.0)
    bool_key: bool = field(default=True)
    none_key: Any = field(default=None)
    nested_section: DataclassSubSection = field(default_factory=DataclassSubSection)


@dataclass
class DefaultSettingsAsDataClass:
    section: DataclassSection = field(default_factory=DataclassSection)


# Dataclass settings for testing INI. INI does not permit nested sections, so we need a flat structure specifically for INI
@dataclass
class INIDataclassSection:
    string_key: str = field(default="value")
    int_key: int = field(default=1)
    float_key: float = field(default=1.0)
    bool_key: bool = field(default=True)
    none_key: Any = field(default=None)


@dataclass
class DefaultINIFileSettingsAsDataClass:
    section: INIDataclassSection = field(default_factory=INIDataclassSection)


# Dataclass settings for testing TOML. TOML only permits nested "tables" (dictionaries), so we need a structure specifically for TOML
@dataclass
class TOMLDataclassSubSection:
    string_key_in_sub_section: str = field(default="value")


@dataclass
class TOMLDataclassSection:
    string_key: str = field(default="value")
    dict_key: Dict[str, Any] = field(
        default_factory=lambda: {"key1": "value1", "key2": "value2"}
    )
    int_key: int = field(default=1)
    float_key: float = field(default=1.0)
    bool_key: bool = field(default=True)
    none_key: Any = field(default=None)
    nested_section: TOMLDataclassSubSection = field(
        default_factory=TOMLDataclassSubSection
    )


@dataclass
class DefaultTOMLFileSettingsAsDataClass:
    section: TOMLDataclassSection = field(default_factory=TOMLDataclassSection)


#####################################################################################


# Class settings for testing JSON and YAML
class ClassSubSection:
    def __init__(self) -> None:
        self.string_key_in_sub_section: str = "value"


class ClassSection:
    def __init__(self) -> None:
        self.string_key: str = "value"
        self.list_key: List[Union[str, object]] = ["value1", ClassSubSection()]
        self.dict_key: Dict[str, Any] = {"key1": "value1", "key2": ClassSubSection()}
        self.int_key: int = 1
        self.float_key: float = 1.0
        self.bool_key: bool = True
        self.none_key: Any = None
        self.nested_section: ClassSubSection = ClassSubSection()


class DefaultSettingsAsClass:
    def __init__(self, dict: Dict = {}) -> None:
        self.section: ClassSection = ClassSection()
        self.__dict__.update(dict)


# Class settings for testing INI. INI does not permit nested sections, so we need a flat structure specifically for INI
class INIClassSection:
    def __init__(self) -> None:
        self.string_key: str = "value"
        self.int_key: int = 1
        self.float_key: float = 1.0
        self.bool_key: bool = True
        self.none_key: Any = None


class DefaultINIFileSettingsAsClass:
    def __init__(self, dict: Dict = {}) -> None:
        self.section: INIClassSection = INIClassSection()
        self.__dict__.update(dict)


# Class settings for testing TOML. TOML only permits nested "tables" (dictionaries), so we need a structure specifically for TOML
class TOMLClassSubSection:
    def __init__(self) -> None:
        self.string_key_in_sub_section: str = "value"


class TOMLClassSection:
    def __init__(self) -> None:
        self.string_key: str = "value"
        self.dict_key: Dict[str, Any] = {"key1": "value1", "key2": "value2"}
        self.int_key: int = 1
        self.float_key: float = 1.0
        self.bool_key: bool = True
        self.none_key: Any = None
        self.nested_section: TOMLClassSubSection = TOMLClassSubSection()


class DefaultTOMLFileSettingsAsClass:
    def __init__(self, dict: Dict = {}) -> None:
        self.section: TOMLClassSection = TOMLClassSection()
        self.__dict__.update(dict)
