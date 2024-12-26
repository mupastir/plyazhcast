from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    openai_api_key: str
    openai_model: str
    aws_key_id_s3: str
    aws_secret_key_s3: str
    aws_bucket_name: str
    cloudflare_account_id: str


settings = Settings()
