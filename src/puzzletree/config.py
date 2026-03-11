"""Configuration management for Puzzletree."""

from pydantic import BaseModel


class Config(BaseModel):
    """Configuration model for Puzzletree."""

    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
