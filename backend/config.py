"""Configurações via variáveis de ambiente."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Orquestrador (mapeado via ALFRED_ prefix manualmente)
    HOST: str = "0.0.0.0"
    PORT: int = 8765
    SECRET_TOKEN: str = "mude-isso-em-producao"

    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GITHUB_TOKEN: str = ""

    VPS_01_HOST: str = ""
    VPS_01_USER: str = "root"
    VPS_01_SSH_KEY_PATH: str = "~/.ssh/id_rsa"

    COOLIFY_API_URL: str = ""
    COOLIFY_API_TOKEN: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    ALFRED_HOST: str = "0.0.0.0"
    ALFRED_PORT: int = 8765
    ALFRED_SECRET_TOKEN: str = "mude-isso-em-producao"

    @property
    def effective_host(self) -> str:
        return self.ALFRED_HOST

    @property
    def effective_port(self) -> int:
        return self.ALFRED_PORT

    @property
    def effective_token(self) -> str:
        return self.ALFRED_SECRET_TOKEN


settings = Settings()
