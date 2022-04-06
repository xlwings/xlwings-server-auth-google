from functools import lru_cache

import httpx
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel

from .. import settings

# Replace '.directory_env' with '.directory_google'
# to query groups from Google Directory. Alternatively,
# provide your own implementation for Okta, Azure AD, LDAP, etc.
from .directory_env import is_member

# See: https://developers.google.com/identity/protocols/oauth2/openid-connect#discovery
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


class User(BaseModel):
    id: str
    email: str
    email_verified: bool
    domain: str


@lru_cache()
def get_google_userinfo_url():
    response = httpx.get(GOOGLE_DISCOVERY_URL)
    return response.json()["userinfo_endpoint"]


async def authenticate(
    oauth_token: str = Security(APIKeyHeader(name="Authorization")),
) -> User:
    """Decodes `ScriptApp.getOAuthToken()` from Google Apps Script (an OAuth 2.0 access
    token) and returns a `User` object if successful, otherwise raises 401.
    """
    userinfo_url = get_google_userinfo_url()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            userinfo_url, headers={"Authorization": f"Bearer {oauth_token}"}
        )
    if response.status_code == 200:
        userinfo = response.json()
        user = User(
            id=userinfo["sub"],
            email=userinfo["email"],
            email_verified=userinfo["email_verified"],
            domain=userinfo.get("hd")
            if userinfo.get("hd")
            else userinfo["email"].split("@")[1],
        )
        if user.domain in settings.google_allowed_domains and user.email_verified:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OAuth Token",
        )


async def authorize(
    security_scopes: SecurityScopes = None, user: User = Depends(authenticate)
) -> User:
    """Checks if the authenticated user is authorized for the required scope and
    returns the User. Use as follows:

    ```
    async def myendpoint(current_user: User = Security(authorize, scopes=["myscope"])):
        pass
    ```

    If you're only interested in getting the `User` object, you can leave away the
    scopes or use `authenticate` instead.
    """
    if security_scopes.scopes:
        for scope in security_scopes.scopes:
            if is_member(email=user.email, group=scope):
                return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Missing authorization! Required scope: "
            f"{' or '.join(security_scopes.scopes)}",
        )
    else:
        return user
