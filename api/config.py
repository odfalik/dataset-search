from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Dataset Search"
    PORT: int = 8000
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str = "dataset-search"

    # Whether to process datasets on startup
    PROCESS_DATASETS: bool = False

    # Load settings from the .env file
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore
