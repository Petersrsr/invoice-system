from pydantic_settings import BaseSettings, SettingsConfigDict


# 应用运行配置，统一从 .env 读取并提供默认值。
class Settings(BaseSettings):
    app_name: str = "Invoice Reimbursement API"
    app_env: str = "dev"

    llm_api_base: str = "https://api.deepseek.com"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"

    database_url: str = "sqlite:///./invoice.db"
    archive_dir: str = "./archives"
    source_dir: str = "./source_files"
    preview_dir: str = "./previews"
    meta_dir: str = "./meta"

    # 后端默认在 backend 目录启动，因此 .env 相对 backend 生效。
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
