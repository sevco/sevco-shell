from dataclasses import dataclass
from typing import List, Optional

from sevco_shell.clients.models import with_dict


@dataclass
class GenericOAuthCredentials(with_dict):
    expires_in: int
    expires: int
    access_token: str
    token_type:  str
    id_token: Optional[str] = None
    scope: Optional[str] = None
    api_domain:  Optional[str] = None
    refresh_token: Optional[str] = None
    ext_expires_in: Optional[int] = None


@dataclass
class OAuthSettings(with_dict):
    client_id: str
    client_secret: str
    scope: List[str]
    initial_url: str
    token_url: str
    revoke_url: str
    finalize_url: Optional[str] = None


@dataclass
class SourceOAuthSettings(with_dict):
    source_id: str
    settings: OAuthSettings
