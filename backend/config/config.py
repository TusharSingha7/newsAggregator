from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    news_api_key: str
    redis_url: str
    app_env: str = "production"


settings = Settings()


class Source(BaseModel):
    id: str | None = None
    name: str


class NewsInstance(BaseModel):
    source: Source
    author: str | None = None
    title: str
    description: str | None = None
    url: HttpUrl | None = None
    urlToImage: HttpUrl | None = None
    publishedAt: str
    content: str | None = None
    embedding: Optional[list[float]] = None


class NewsApiResponse(BaseModel):
    status: str = Field(description="status of Api call")
    totalResults: int = Field(description="total count of returned news")
    articles: list[NewsInstance]


class UserData(BaseModel):
    userId: str = Field(description="unique user identification string")
    embedding: list[float] = Field(..., description="news embedding to store ")
