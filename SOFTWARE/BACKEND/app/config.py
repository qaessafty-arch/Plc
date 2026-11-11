from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./spm_dev.sqlite3"
    api_token: str = ""                 # empty = write endpoints disabled
    cors_origins: str = "http://localhost:5173"
    plc_source: str = "simulated"       # simulated | opcua | none
    opcua_url: str = "opc.tcp://192.168.10.10:4840"
    opcua_user: str = ""
    opcua_password: str = ""
    poll_period_s: float = 1.0
    sample_period_s: float = 10.0


settings = Settings()
