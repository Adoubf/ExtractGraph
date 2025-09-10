from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    base_url: str = "your_base_url_here"
    api_key: str = "your_api_key_here"
    model_id: str = "your_model_id_here"

    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
        
        
settings = Settings()
    