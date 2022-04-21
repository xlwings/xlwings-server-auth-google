from typing import Dict, List, Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    directory: str = "env"
    google_allowed_domains: List
    group_admin: Optional[List]
    google_delegate_email: Optional[str]
    google_service_account_info: Optional[Dict]
    scopes: List = ["group_admin"]

    class Config:
        env_file = ".env"


settings = Settings()
