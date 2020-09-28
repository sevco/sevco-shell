from dataclasses import dataclass

from sevco_shell.clients.tenant.models import Organization
from sevco_shell.config.credentials import ApiCredentials


@dataclass
class Config:
    credentials: ApiCredentials
    org: Organization
