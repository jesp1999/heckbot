"""Configuration for the bot."""
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Settings for the bot."""
    aws_access_key_id: str = Field(env='AWS_ACCESS_KEY_ID', default='')
    aws_default_region: str = Field(env='AWS_DEFAULT_REGION', default='')
    aws_host: str = Field(env='AWS_HOST', default='')
    aws_secret_access_key: str = Field(env='AWS_SECRET_ACCESS_KEY', default='')
    bot_token: str = Field(env='DISCORD_TOKEN', default='')
    declare_global_commands: int = Field(env='DECLARE_GLOBAL_COMMANDS',
                                         default=0)
    heckbot_secret_key: str = Field(env='HECKBOT_SECRET_KEY', default='')
    owner_ids: list[int] = Field(env='OWNER_IDS', default_factory=list)
    prefix: str = Field(env='PREFIX', default='/')
    pick_server_url: str = Field(env='PICK_SERVER_URL',
                                 default='http://localhost:8080')
    tenor_api_key: str = Field(env='TENOR_API_KEY', default='')

    class Config(BaseSettings.Config):
        env_file = '.env'
        case_sensitive = False
