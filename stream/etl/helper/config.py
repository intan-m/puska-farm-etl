from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings


# Definition
class EnvConfig(BaseSettings):
    DWH_DIALECT: str = Field(alias="DWH_DIALECT", default="postgresql")
    DWH_USERNAME: str = Field(alias="DWH_USERNAME")
    DWH_PASSWORD: SecretStr = Field(alias="DWH_PASSWORD")
    DWH_HOSTNAME: str = Field(alias="DWH_HOSTNAME")
    DWH_PORT: str = Field(alias="DWH_PORT")
    DWH_NAME: str = Field(alias="DWH_NAME")
    KAFKA_HOSTNAME: str = Field(alias="KAFKA_HOSTNAME")
    KAFKA_PORT: str = Field(alias="KAFKA_PORT")
    KAFKA_TOPIC: str = Field(alias="KAFKA_TOPIC")
    WS_CONNECT_HOSTNAME: str = Field(alias="WS_CONNECT_HOSTNAME")
    WS_PORT: int = Field(alias="WS_PORT")


# Implementation
CONFIG = EnvConfig()
