from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import RedirectResponse

from app.services.url import get_short_url_by_code
from app.services.click import log_click

router = APIRouter(tags=["Redirect"])


@router.get("/{short_code}")
async def redirect_to_url(short_code: str, request: Request):
    """
    Redirect to the original URL.
    Uses 302 redirect to preserve analytics tracking.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    if not short_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has been deactivated"
        )

    # Check expiration
    if short_url.expiration and datetime.now(timezone.utc) > short_url.expiration:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has expired"
        )

    # Log the click asynchronously (fire and forget pattern)
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    try:
        await log_click(
            short_url=short_url,
            ip_address=client_ip,
            user_agent=user_agent,
            referrer=referrer
        )
    except Exception:
        pass  # Don't fail redirect if logging fails

    # 302 redirect (not 301) to ensure we always track clicks
    return RedirectResponse(
        url=short_url.original_url,
        status_code=status.HTTP_302_FOUND
    )


@router.get("/{short_code}/preview")
async def get_url_preview_page(short_code: str):
    """
    Get URL preview information without redirecting.
    Useful for preview cards/tooltips.
    """
    short_url = await get_short_url_by_code(short_code)

    if not short_url or not short_url.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="URL not found"
        )

    # Check expiration
    if short_url.expiration and datetime.now(timezone.utc) > short_url.expiration:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="URL has expired"
        )

    return {
        "original_url": short_url.original_url,
        "title": short_url.preview_title,
        "description": short_url.preview_description,
        "image": short_url.preview_image
    }
