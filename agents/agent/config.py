from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PORT: int = 8080
    SHARED_SECRET: str = "agentsharedsecretforauthandencryption"


agent_settings = AgentSettings()
