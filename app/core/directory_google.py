import logging

import googleapiclient.errors
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .. import settings

logger = logging.getLogger(__name__)


def is_member(email: str, group: str, **kwargs) -> bool:
    scopes = [
        "https://www.googleapis.com/auth/admin.directory.group.readonly",
        "https://www.googleapis.com/auth/admin.directory.group.member.readonly",
    ]
    if kwargs.get("http"):
        # HttpMock for unit test
        service = build("admin", "directory_v1", http=kwargs["http"])
    else:
        credentials = Credentials.from_service_account_info(
            info=settings.google_service_account_info, scopes=scopes
        )
        delegated_credentials = credentials.with_subject(settings.google_delegate_email)
        service = build("admin", "directory_v1", credentials=delegated_credentials)
    try:
        results = (
            service.members()
            .hasMember(
                groupKey=group,
                memberKey=email,
            )
            .execute()
        )
        return results["isMember"]
    except googleapiclient.errors.HttpError as e:
        logger.error(
            f"Failed to look up user '{email}' in group '{group}': "
            f"{e.reason} (Error {e.status_code})"
        )
        return False
