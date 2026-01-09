"""Tests for URL shortening endpoints."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.url import ShortURL
from app.models.user import User
from app.services.url import generate_short_code, is_valid_custom_alias


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    user = MagicMock(spec=User)
    user.id = "507f1f77bcf86cd799439011"
    user.email = "test@example.com"
    user.is_active = True
    user.is_admin = False
    user.created_at = datetime.now(UTC)
    return user


@pytest.fixture
def auth_token(mock_user):
    """Create a valid JWT token for testing."""
    return create_access_token(data={"sub": mock_user.email, "user_id": str(mock_user.id)})


@pytest.fixture
def mock_short_url(mock_user):
    """Create a mock short URL for testing."""
    url = MagicMock(spec=ShortURL)
    url.id = "607f1f77bcf86cd799439022"
    url.original_url = "https://example.com/very/long/url/path"
    url.short_code = "abc123x"
    url.clicks = 0
    url.is_active = True
    url.expiration = None
    url.created_at = datetime.now(UTC)
    url.preview_title = "Example Site"
    url.preview_description = "Example description"
    url.preview_image = "https://example.com/image.png"
    url.user = MagicMock()
    url.user.id = mock_user.id
    url.user.ref = MagicMock()
    url.user.ref.id = mock_user.id
    return url


class TestShortCodeGeneration:
    """Tests for short code generation utilities."""

    def test_generate_short_code_default_length(self):
        """Test short code generation with default length."""
        code = generate_short_code()
        assert len(code) == 7  # Default length from settings
        assert code.isalnum()

    def test_generate_short_code_custom_length(self):
        """Test short code generation with custom length."""
        code = generate_short_code(length=10)
        assert len(code) == 10

    def test_generate_short_code_uniqueness(self):
        """Test that generated codes are reasonably unique."""
        codes = [generate_short_code() for _ in range(100)]
        unique_codes = set(codes)
        # With base62 and 7 chars, collisions should be extremely rare
        assert len(unique_codes) == 100


class TestCustomAliasValidation:
    """Tests for custom alias validation."""

    def test_valid_alias(self):
        """Test valid custom aliases."""
        assert is_valid_custom_alias("mylink") is True
        assert is_valid_custom_alias("my-link") is True
        assert is_valid_custom_alias("my_link") is True
        assert is_valid_custom_alias("MyLink123") is True

    def test_alias_too_short(self):
        """Test alias that is too short."""
        assert is_valid_custom_alias("abc") is False  # Less than 4 chars

    def test_alias_too_long(self):
        """Test alias that is too long."""
        assert is_valid_custom_alias("a" * 21) is False  # More than 20 chars

    def test_invalid_characters(self):
        """Test alias with invalid characters."""
        assert is_valid_custom_alias("my link") is False  # Space
        assert is_valid_custom_alias("my.link") is False  # Dot
        assert is_valid_custom_alias("my@link") is False  # @ symbol

    def test_empty_alias(self):
        """Test empty alias."""
        assert is_valid_custom_alias("") is False
        assert is_valid_custom_alias(None) is False


class TestShortenEndpoint:
    """Tests for the shorten URL endpoint."""

    @pytest.mark.asyncio
    async def test_shorten_url_success(self, mock_user, auth_token):
        """Test successful URL shortening."""
        with patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find:
            with patch("app.api.urls.create_short_url", new_callable=AsyncMock) as mock_create:
                mock_find.return_value = mock_user
                mock_short = MagicMock()
                mock_short.id = "607f1f77bcf86cd799439022"
                mock_short.original_url = "https://example.com/long"
                mock_short.short_code = "abc123x"
                mock_short.clicks = 0
                mock_short.expiration = None
                mock_short.created_at = datetime.now(UTC)
                mock_short.preview_title = None
                mock_short.preview_description = None
                mock_short.preview_image = None
                mock_create.return_value = mock_short

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/urls/shorten",
                        json={"original_url": "https://example.com/long"},
                        headers={"Authorization": f"Bearer {auth_token}"},
                    )

                assert response.status_code == 201
                data = response.json()
                assert data["short_code"] == "abc123x"
                assert "short_url" in data

    @pytest.mark.asyncio
    async def test_shorten_url_with_custom_alias(self, mock_user, auth_token):
        """Test URL shortening with custom alias."""
        with patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find:
            with patch("app.api.urls.create_short_url", new_callable=AsyncMock) as mock_create:
                mock_find.return_value = mock_user
                mock_short = MagicMock()
                mock_short.id = "607f1f77bcf86cd799439022"
                mock_short.original_url = "https://example.com/long"
                mock_short.short_code = "myalias"
                mock_short.clicks = 0
                mock_short.expiration = None
                mock_short.created_at = datetime.now(UTC)
                mock_short.preview_title = None
                mock_short.preview_description = None
                mock_short.preview_image = None
                mock_create.return_value = mock_short

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.post(
                        "/api/v1/urls/shorten",
                        json={
                            "original_url": "https://example.com/long",
                            "custom_alias": "myalias",
                        },
                        headers={"Authorization": f"Bearer {auth_token}"},
                    )

                assert response.status_code == 201
                data = response.json()
                assert data["short_code"] == "myalias"

    @pytest.mark.asyncio
    async def test_shorten_url_without_auth(self):
        """Test that shortening requires authentication."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/urls/shorten", json={"original_url": "https://example.com/long"}
            )

        assert response.status_code == 401


class TestListURLsEndpoint:
    """Tests for listing user URLs."""

    @pytest.mark.asyncio
    async def test_list_urls_success(self, mock_user, auth_token, mock_short_url):
        """Test listing user's URLs."""
        with patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find:
            with patch("app.api.urls.get_user_urls", new_callable=AsyncMock) as mock_list:
                mock_find.return_value = mock_user
                mock_list.return_value = [mock_short_url]

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get(
                        "/api/v1/urls", headers={"Authorization": f"Bearer {auth_token}"}
                    )

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 1
                assert data[0]["short_code"] == "abc123x"

    @pytest.mark.asyncio
    async def test_list_urls_empty(self, mock_user, auth_token):
        """Test listing URLs when user has none."""
        with patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find:
            with patch("app.api.urls.get_user_urls", new_callable=AsyncMock) as mock_list:
                mock_find.return_value = mock_user
                mock_list.return_value = []

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.get(
                        "/api/v1/urls", headers={"Authorization": f"Bearer {auth_token}"}
                    )

                assert response.status_code == 200
                data = response.json()
                assert len(data) == 0


class TestDeleteURLEndpoint:
    """Tests for deleting URLs."""

    @pytest.mark.asyncio
    async def test_delete_url_success(self, mock_user, auth_token):
        """Test successful URL deletion."""
        with patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find:
            with patch("app.api.urls.delete_short_url", new_callable=AsyncMock) as mock_delete:
                mock_find.return_value = mock_user
                mock_delete.return_value = True

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.delete(
                        "/api/v1/urls/abc123x", headers={"Authorization": f"Bearer {auth_token}"}
                    )

                assert response.status_code == 200
                data = response.json()
                assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_delete_url_not_found(self, mock_user, auth_token):
        """Test deleting a non-existent URL."""
        with patch("app.core.security.User.find_one", new_callable=AsyncMock) as mock_find:
            with patch("app.api.urls.delete_short_url", new_callable=AsyncMock) as mock_delete:
                mock_find.return_value = mock_user
                mock_delete.return_value = False

                transport = ASGITransport(app=app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    response = await client.delete(
                        "/api/v1/urls/nonexistent",
                        headers={"Authorization": f"Bearer {auth_token}"},
                    )

                assert response.status_code == 404


class TestPreviewEndpoint:
    """Tests for URL preview fetching."""

    @pytest.mark.asyncio
    async def test_preview_url(self):
        """Test fetching URL preview metadata."""
        with patch("app.api.urls.fetch_preview_service", new_callable=AsyncMock) as mock_preview:
            from app.schemas.url import URLPreview

            mock_preview.return_value = URLPreview(
                title="Example Site",
                description="Example description",
                image="https://example.com/image.png",
                url="https://example.com",
            )

            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/urls/preview", params={"url": "https://example.com"}
                )

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Example Site"
            assert data["description"] == "Example description"
