"""
Application configuration module.

This module defines the Settings class, which loads environment variables
using Pydantic Settings. It is responsible for providing the DATABASE_URL
used by the application and by test workflows (e.g., pytest on GitHub Actions).
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
        DATABASE_URL (str): The database connection string. This value is
            typically provided via a `.env` file during local development,
            or via environment variables in CI/CD environments such as
            GitHub Actions (e.g., for pytest workflows).

    Notes:
        - `model_config` specifies that Pydantic should load variables from
          a `.env` file when running locally.
        - In GitHub Actions, you can set DATABASE_URL using workflow `env`
          or `secrets` so pytest can initialize the database correctly.
    """

    model_config = ConfigDict(env_file=".env")
    DATABASE_URL: str
    JWT_SECRET_KEY: str | None = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
