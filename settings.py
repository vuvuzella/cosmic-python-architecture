from pydantic import BaseSettings, Field, stricturl, validator
from typing import Dict


class Settings(BaseSettings):
    # DB Connection
    DB_PROTOCOL: str = "postgresql+psycopg2"
    DB_USERNAME: str = "Nope"
    DB_PASSWORD: str = "Nope"
    DB_HOST: str = "Nope"
    DB_PORT: int = 5435
    DB_NAME: str = "cosmic_python_db"
    # DB_DSN_QUERY: str = Field("sslmode=requre", env=[""])
    # DB_DSB: stricturl(tld_required=False, allowed_schemes={"postgresql", "postgresql+asyncpg", "postgresql+psycopg", "postgresql+psycopg2"}) = Field(None, env=[""])
    DB_DSN: str = ""

    @validator("DB_DSN", pre=True, always=True)
    def make_dsn(cls, v, values: Dict[str, str | int], **kwargs):
        return (
            v
            or f"{values.get('DB_PROTOCOL')}://{values.get('DB_USERNAME')}:{values.get('DB_PASSWORD')}@{values.get('DB_HOST')}:{values.get('DB_PORT')}/{values.get('DB_NAME')}"
        )


global_settings = Settings()
