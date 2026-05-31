# from pydantic_settings import BaseSettings
# from typing import Optional

# class Settings(BaseSettings):
#     DATABASE_URL: str
#     QDRANT_URL: str
#     QDRANT_COLLECTION: str = "rag_documents"
#     OPENAI_API_KEY: str
#     COHERE_API_KEY: str
#     LANGSMITH_API_KEY: Optional[str] = None
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

#     class Config:
#         env_file = ".env"

# settings = Settings()



# test only above is original
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # DB
    DATABASE_URL: str

    # Qdrant
    QDRANT_URL: str
    QDRANT_COLLECTION: str

    # AI
    COHERE_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # LangSmith
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_TRACING: Optional[bool] = None
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    # Auth
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = ".env"

settings = Settings()