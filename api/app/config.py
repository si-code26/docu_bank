from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    database_url: str="postgresql+asyncpg://docubank:docubank@localhost:5432/docubank"
    openai_api_key:str
    s3_endpoint:str|None=None
    s3_bucket:str="docubank-uploads"
    embed_model:str="text-embedding-3-small"
    answer_model:str="gpt-4o-mini"
    redis_url: str="redis://localhost:6379/0"
    sqs_endpoint:str|None=None
    ingest_queue_url:str
    aws_region:str="us-east-1"
    cognito_user_pool_id:str="us-east-1_Q9piP8XUp"
    cognito_client_id:str="3pp56kb338fcvol3b0gmg6hqa0"

settings=Settings()
