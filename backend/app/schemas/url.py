from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional


class URLCreate(BaseModel):
    original_url: str = Field(..., description="The original URL to shorten")
    custom_alias: Optional[str] = Field(
        None,
        min_length=4,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Custom alias for the short URL"
    )
    expiration_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Number of days until URL expires"
    )


class URLResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    short_url: str
    clicks: int
    expiration: Optional[datetime]
    created_at: datetime
    preview_title: Optional[str] = None
    preview_description: Optional[str] = None
    preview_image: Optional[str] = None


class URLStats(BaseModel):
    short_code: str
    original_url: str
    total_clicks: int
    clicks_today: int
    clicks_this_week: int
    top_referrers: list[dict]
    clicks_by_country: list[dict]
    clicks_by_device: list[dict]
    clicks_over_time: list[dict]


class URLPreview(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    url: str
