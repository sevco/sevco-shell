from dataclasses import dataclass
import datetime
from sevco_shell.clients.models import with_dict
from typing import List, Optional


@dataclass
class Organization(with_dict):
    id: str
    created: datetime.datetime
    org_name: str


@dataclass
class CreateOrganizationResponse(with_dict):
    org_id: str
    created: datetime.datetime
    org_name: str


@dataclass
class OrgRoles(with_dict):
    id: str
    roleid: Optional[str]


@dataclass
class UserInvite(with_dict):
    email: str
    orgs: List[OrgRoles]


@dataclass
class User(with_dict):
    email: str
    name: str
    nickname: str
    picture: str
    roles: List[str]
    created: datetime.datetime


@dataclass
class Role(with_dict):
    id: str
    name: str
    description: str
