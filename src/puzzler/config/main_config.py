"""Configuration management for puzzler."""

# Template note: These imports are kept for potential future use in template expansions
# They may be used conditionally based on template variables or in extended configurations
import json  # noqa: F401 - Reserved for future JSON config file handling
from pathlib import Path  # noqa: F401 - Reserved for future path-based config loading

from pydantic import (  # noqa: F401 - Reserved for future field validation
    Field,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,  # noqa: F401 - Reserved for future JSON config source
    PydanticBaseSettingsSource,  # noqa: F401 - Reserved for future custom config sources
    SettingsConfigDict,
)

from puzzler._version import get_version


class Config(BaseSettings):
    """Configuration class for loading environment variables.

    This class uses pydantic and pydantic-settings to define and load environment variables.
    It supports loading from .env and .env.prod files (lowest to highest priority),
    and uses field validators for data validation.
    """

    schema_version: str = "1.0.0"
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.dev", ".env.prod"),
        env_file_encoding="utf-8",
        json_file="puzzler_config.json",
    )
    # Configurations for the application
    app_name: str = "puzzler"
    app_description: str = "Puzzle reconstruction experiments and CLI tooling."
    app_author: str = "lalmei"
    app_version: str = get_version()
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
