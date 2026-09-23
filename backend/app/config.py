from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    cors_origins: str = "http://localhost:5173"
    admin_api_key: str = "change-me-in-production"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        local_origins = {"http://localhost:5173", "http://127.0.0.1:5173"}
        if local_origins.intersection(origins):
            origins.extend(local_origins.difference(origins))
        return origins


settings = Settings()
