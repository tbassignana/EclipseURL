from datetime import datetime

from pydantic import BaseModel, Field


class URLCreate(BaseModel):
    original_url: str = Field(..., description="The original URL to shorten")
    custom_alias: str | None = Field(
        None,
        min_length=4,
        max_length=20,
        pattern="^[a-zA-Z0-9_-]+$",
        description="Custom alias for the short URL",
    )
    expiration_days: int | None = Field(
        None, ge=1, le=365, description="Number of days until URL expires"
    )


class URLResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    short_url: str
    clicks: int
    expiration: datetime | None
    created_at: datetime
    preview_title: str | None = None
    preview_description: str | None = None
    preview_image: str | None = None


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
    title: str | None = None
    description: str | None = None
    image: str | None = None
    url: str
