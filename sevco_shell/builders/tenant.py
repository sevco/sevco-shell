from typing import Optional

from sevco_shell.builders.builder import Builder
from sevco_shell.clients.tenant.client import TenantClient
from sevco_shell.clients.tenant.models import (CreateOrganizationResponse,
                                               OrgRoles,
                                               UserInvite)
from sevco_shell.config import Config
from sevco_shell.config.credentials import ApiCredentials


class OrgBuilder(Builder):
    def __init__(self, credentials: ApiCredentials):
        self.client = TenantClient(
            api_host=credentials.api_host, auth_token=credentials.auth_token)
        self.org_name = None

    def from_user(self) -> 'OrgBuilder':
        try:
            self.org_name = self._from_user()
        except KeyboardInterrupt:
            print()

        return self

    def _from_user(self) -> str:
        org_name = self.get_input("Org Name")

        return org_name

    def build(self) -> Optional[CreateOrganizationResponse]:
        if self.org_name:
            org = self.client.org_create(self.org_name)
            print(f"Created org {org.org_name} (id: {org.org_id})")
            return org

        return None


class AddUserBuilder(Builder):
    def __init__(self, config: Config):
        self.client = TenantClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.email = None

    def from_user(self) -> 'AddUserBuilder':
        try:
            self.email = self._from_user()
        except KeyboardInterrupt:
            pass

        return self

    def _from_user(self) -> str:
        return self.get_input("Email", required=True)

    def build(self) -> Optional[str]:
        if self.email:
            email = self.client.add_user(self.email)
            print("User added to org")
            return email

        return None
