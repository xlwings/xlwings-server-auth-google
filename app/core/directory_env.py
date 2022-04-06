from .. import settings


def is_member(email: str, group: str) -> bool:
    for key, values in settings:
        if key.lower() == group.lower():
            if values and email in values:
                return True
