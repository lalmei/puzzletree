"""Configuration management for fun."""

from pydantic import BaseModel


class Config(BaseModel):
    """Configuration model for fun."""

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
