class SettingsException(Exception):
    """Base exception class for settings-related errors."""

    pass


class InvalidPathError(SettingsException):
    """Exception raised when an invalid path is provided."""

    pass


class UnsupportedFormatError(SettingsException):
    """Exception raised when an unsupported settings file format is specified."""

    pass


class MissingDependencyError(SettingsException):
    """Exception raised when a required dependency for a settings format is missing."""

    pass


class SanitizationError(SettingsException):
    """Exception raised during sanitization of settings data."""

    pass


class SaveError(SettingsException):
    """Exception raised when saving settings fails."""

    pass


class LoadError(SettingsException):
    """Exception raised when loading settings fails."""

    pass
