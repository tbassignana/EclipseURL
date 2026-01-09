from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.security import get_current_user
from app.models.url import ShortURL
from app.models.user import User
from app.schemas.url import URLCreate, URLPreview, URLResponse, URLStats
from app.services.url import (
    create_short_url,
    delete_short_url,
)
from app.services.url import fetch_url_preview as fetch_preview_service
from app.services.url import (
    get_short_url_by_code,
    get_url_stats,
    get_user_urls,
)

router = APIRouter(prefix="/urls", tags=["URLs"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/shorten", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.RATE_LIMIT_SHORTEN)
async def shorten_url(
    request: Request, url_data: URLCreate, current_user: User = Depends(get_current_user)
):
    """
    Create a shortened URL.

    - **original_url**: The URL to shorten
    - **custom_alias**: Optional custom alias (4-20 chars, alphanumeric, dash, underscore)
    - **expiration_days**: Optional days until expiration (1-365)
    """
    try:
        short_url = await create_short_url(url_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    return URLResponse(
        id=str(short_url.id),
        original_url=short_url.original_url,
        short_code=short_url.short_code,
        short_url=f"{settings.BASE_URL}/{short_url.short_code}",
        clicks=short_url.clicks,
        expiration=short_url.expiration,
        created_at=short_url.created_at,
        preview_title=short_url.preview_title,
        preview_description=short_url.preview_description,
        preview_image=short_url.preview_image,
    )


@router.get("", response_model=list[URLResponse])
async def list_user_urls(
    current_user: User = Depends(get_current_user), skip: int = 0, limit: int = 100
):
    """
    List all URLs created by the current user.
    """
    urls = await get_user_urls(current_user, skip=skip, limit=limit)

    return [
        URLResponse(
            id=str(url.id),
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=f"{settings.BASE_URL}/{url.short_code}",
            clicks=url.clicks,
            expiration=url.expiration,
            created_at=url.created_at,
            preview_title=url.preview_title,
            preview_description=url.preview_description,
            preview_image=url.preview_image,
        )
        for url in urls
    ]


@router.get("/preview", response_model=URLPreview)
async def get_url_preview(url: str):
    """
    Fetch preview metadata for a URL (Open Graph data).
    """
    preview = await fetch_preview_service(url)
    return preview


@router.get("/{short_code}/stats", response_model=URLStats)
async def get_url_statistics(short_code: str, current_user: User = Depends(get_current_user)):
    """
    Get detailed statistics for a shortened URL.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url or not short_url.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    # Verify ownership (unless admin)
    if not current_user.is_admin:
        await short_url.fetch_link(ShortURL.user)
        if short_url.user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this URL"
            )

    return await get_url_stats(short_url)


@router.get("/{short_code}", response_model=URLResponse)
async def get_url_details(short_code: str, current_user: User = Depends(get_current_user)):
    """
    Get details of a specific shortened URL.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url or not short_url.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found")

    # Verify ownership (unless admin)
    if not current_user.is_admin:
        await short_url.fetch_link(ShortURL.user)
        if short_url.user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this URL"
            )

    return URLResponse(
        id=str(short_url.id),
        original_url=short_url.original_url,
        short_code=short_url.short_code,
        short_url=f"{settings.BASE_URL}/{short_url.short_code}",
        clicks=short_url.clicks,
        expiration=short_url.expiration,
        created_at=short_url.created_at,
        preview_title=short_url.preview_title,
        preview_description=short_url.preview_description,
        preview_image=short_url.preview_image,
    )


@router.delete("/{short_code}", status_code=status.HTTP_200_OK)
async def delete_url(short_code: str, current_user: User = Depends(get_current_user)):
    """
    Delete a shortened URL (soft delete).
    """
    success = await delete_short_url(short_code, current_user)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="URL not found or not authorized"
        )

    return {"message": "URL deleted successfully"}
