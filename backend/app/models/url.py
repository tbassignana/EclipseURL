from beanie import Document, Indexed, Link
from pydantic import Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import User


class ShortURL(Document):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "original_url": "https://example.com/very/long/url",
                "short_code": "abc123",
                "clicks": 0,
                "is_active": True
            }
        }
    )

    original_url: str
    short_code: Indexed(str, unique=True)
    user: Link[User]
    custom_alias: Optional[str] = None
    clicks: int = 0
    expiration: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    # URL Preview metadata
    preview_title: Optional[str] = None
    preview_description: Optional[str] = None
    preview_image: Optional[str] = None

    class Settings:
        name = "short_urls"
        use_state_management = True

    @property
    def is_expired(self) -> bool:
        if self.expiration is None:
            return False
        return datetime.utcnow() > self.expiration
