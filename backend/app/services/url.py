import string
import secrets
import re
from datetime import datetime, timedelta, timezone
from typing import Optional
import aiohttp
from bs4 import BeautifulSoup

from app.core.config import settings
from app.models.url import ShortURL
from app.models.user import User
from app.schemas.url import URLCreate, URLPreview

# Base62 character set for URL-safe short codes
BASE62_CHARS = string.digits + string.ascii_lowercase + string.ascii_uppercase


def generate_short_code(length: int = None) -> str:
    """Generate a random base62 short code."""
    if length is None:
        length = settings.SHORT_CODE_LENGTH
    return ''.join(secrets.choice(BASE62_CHARS) for _ in range(length))


async def is_short_code_available(short_code: str) -> bool:
    """Check if a short code is available (not already in use)."""
    existing = await ShortURL.find_one({"short_code": short_code})
    return existing is None


async def generate_unique_short_code(max_attempts: int = 10) -> str:
    """Generate a unique short code with collision detection."""
    for _ in range(max_attempts):
        code = generate_short_code()
        if await is_short_code_available(code):
            return code
    raise ValueError("Could not generate unique short code after max attempts")


def is_valid_custom_alias(alias: str) -> bool:
    """Validate custom alias format."""
    if not alias:
        return False
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, alias)) and 4 <= len(alias) <= 20


async def fetch_url_preview(url: str) -> URLPreview:
    """Fetch Open Graph metadata from a URL for preview."""
    preview = URLPreview(url=url)

    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    return preview

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')

                # Try Open Graph tags first
                og_title = soup.find('meta', property='og:title')
                og_desc = soup.find('meta', property='og:description')
                og_image = soup.find('meta', property='og:image')

                if og_title:
                    preview.title = og_title.get('content', '')[:200]
                elif soup.title:
                    preview.title = soup.title.string[:200] if soup.title.string else None

                if og_desc:
                    preview.description = og_desc.get('content', '')[:500]
                else:
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc:
                        preview.description = meta_desc.get('content', '')[:500]

                if og_image:
                    preview.image = og_image.get('content', '')

    except Exception:
        pass  # Return partial preview on error

    return preview


async def create_short_url(
    url_data: URLCreate,
    user: User,
    fetch_preview: bool = True
) -> ShortURL:
    """Create a new shortened URL."""
    # Use custom alias or generate a unique code
    if url_data.custom_alias:
        if not is_valid_custom_alias(url_data.custom_alias):
            raise ValueError("Invalid custom alias format")
        if not await is_short_code_available(url_data.custom_alias):
            raise ValueError("Custom alias is already taken")
        short_code = url_data.custom_alias
    else:
        short_code = await generate_unique_short_code()

    # Calculate expiration date if provided
    expiration = None
    if url_data.expiration_days:
        expiration = datetime.now(timezone.utc) + timedelta(days=url_data.expiration_days)

    # Fetch URL preview metadata
    preview_title = None
    preview_description = None
    preview_image = None

    if fetch_preview:
        try:
            preview = await fetch_url_preview(url_data.original_url)
            preview_title = preview.title
            preview_description = preview.description
            preview_image = preview.image
        except Exception:
            pass  # Continue without preview

    short_url = ShortURL(
        original_url=url_data.original_url,
        short_code=short_code,
        user=user,
        custom_alias=url_data.custom_alias,
        expiration=expiration,
        preview_title=preview_title,
        preview_description=preview_description,
        preview_image=preview_image,
        created_at=datetime.now(timezone.utc)
    )

    await short_url.insert()
    return short_url


async def get_short_url_by_code(short_code: str) -> Optional[ShortURL]:
    """Find a short URL by its short code."""
    return await ShortURL.find_one({"short_code": short_code})


async def get_user_urls(user: User, skip: int = 0, limit: int = 100) -> list[ShortURL]:
    """Get all URLs created by a user."""
    return await ShortURL.find(
        {"user.$id": user.id, "is_active": True}
    ).skip(skip).limit(limit).to_list()


async def delete_short_url(short_code: str, user: User) -> bool:
    """Soft delete a short URL (mark as inactive)."""
    short_url = await get_short_url_by_code(short_code)
    if not short_url:
        return False

    # Check ownership (unless admin)
    if not user.is_admin and short_url.user.ref.id != user.id:
        return False

    short_url.is_active = False
    short_url.updated_at = datetime.now(timezone.utc)
    await short_url.save()
    return True
