import httpx
import pytest
from fastapi.exceptions import HTTPException

from app.core.auth import User, authenticate


@pytest.mark.asyncio
async def test_authenticate_allowed_domain(respx_mock):
    respx_mock.get("https://accounts.google.com/.well-known/openid-configuration").mock(
        return_value=httpx.Response(
            200,
            json={
                "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo"
            },
        )
    )
    respx_mock.get("https://openidconnect.googleapis.com/v1/userinfo").mock(
        return_value=httpx.Response(
            200,
            json={
                "sub": 123,
                "email": "test@test.com",
                "email_verified": True,
                "hd": "test.com",
            },
        )
    )
    assert await authenticate("token") == User(
        id="123", email="test@test.com", email_verified=True, domain="test.com"
    )


@pytest.mark.asyncio
async def test_authenticate_not_allowed_domain(respx_mock):
    respx_mock.get("https://accounts.google.com/.well-known/openid-configuration").mock(
        return_value=httpx.Response(
            200,
            json={
                "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo"
            },
        )
    )
    respx_mock.get("https://openidconnect.googleapis.com/v1/userinfo").mock(
        return_value=httpx.Response(
            200,
            json={
                "sub": 123,
                "email": "test@not-test.com",
                "email_verified": True,
                "hd": "not-test.com",
            },
        )
    )
    with pytest.raises(HTTPException):
        await authenticate("token")
