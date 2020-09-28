import json
from typing import List

from dacite.core import from_dict

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.tenant.models import CreateOrganizationResponse, Organization, Role, User, UserInvite

PLUGIN_URL_ROOT = "/v1/integration/source/plugin"


class TenantClient(SevcoClient):
    def org_list(self) -> List[Organization]:
        resp = self.api_get("/v1/admin/org")

        return [Organization.from_dict(o) for o in json.loads(resp.text)['orgs']]

    def org_create(self, org_name: str) -> CreateOrganizationResponse:
        resp = self.api_post(
            "/v1/admin/org", data=json.dumps({"org_name": org_name}))

        return CreateOrganizationResponse.from_dict(json.loads(resp.text)['org'])

    def org_delete(self, org_id: str) -> None:
        resp = self.api_delete(
            "/v1/admin/org", data=json.dumps({"id": org_id}))

    def list_users(self) -> List[User]:
        resp = self.api_get("/v1/admin/user")

        return [User.from_dict(o) for o in json.loads(resp.text)['items']]

    def get_user(self, email: str) -> User:
        resp = self.api_get(f"/v1/admin/user/{email}")

        return User.from_dict(json.loads(resp.text))

    def add_user(self, email: str) -> str:
        resp = self.api_post(f"/v1/admin/user/{email}")

        return json.loads(resp.text)['user']['email']

    def delete_user(self, email: str):
        self.api_delete(f"/v1/admin/user/{email}")

    def roles(self) -> List[Role]:
        resp = self.api_get("/v1/admin/role")

        return [Role.from_dict(r) for r in json.loads(resp.text)]

    def user_add_role(self, email: str, role_name: str):
        self.api_put(f"/v1/admin/user/{email}/role/{role_name}")

    def user_delete_role(self, email: str, role_name: str):
        self.api_delete(f"/v1/admin/user/{email}/role/{role_name}")

    def service_account_jwt(self, org_id: str) -> str:
        resp = self.api_get(f"/v1/admin/org/{org_id}/account")

        d = json.loads(resp.text)

        return f"{d['token_type']} {d['access_token']}"

    def auth_token(self, org_id: str) -> str:
        resp = self.api_get(f"/v1/admin/org/{org_id}/apikey")

        return json.loads(resp.text)['apiKey']
