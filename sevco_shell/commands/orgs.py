from typing import Union
from pprint import pprint

from sevco_shell.builders.builder import Builder
from sevco_shell.builders.tenant import OrgBuilder
from sevco_shell.clients.tenant.client import TenantClient
from sevco_shell.clients.tenant.models import Organization
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config
from sevco_shell.config.credentials import ApiCredentials
from sevco_shell.scopes.org import OrgScope
from sevco_shell.scopes.scope import CmdResponse, NewScopeResponse, Scope


def OrgsCmd(credentials: ApiCredentials):
    builder = CommandBuilder('orgs', credentials=credentials)

    @builder.from_cls()
    class _OrgsCmd(CommandWithList):
        '''Orgs - manage and interact with organizations and their configurations'''

        def __init__(self, credentials: ApiCredentials):
            super().__init__()
            self.credentials = credentials
            self.client = TenantClient(
                credentials.api_host, credentials.auth_token)

        def default(self, line: str) -> Union[bool, CmdResponse]:
            try:
                idx = int(line)
                return self._do_select(idx)
            except IndexError as e:
                print(str(e))
                return False
            except ValueError:
                pass

            return super().default(line)

        def things_header(self):
            return [("Org", 32), ("Id", 40)]


        def get_things(self):
            return sorted(self.client.org_list(), key=lambda x: x.org_name)

        def format_thing(self, org: Organization) -> str:
            return f"{org.org_name.rjust(32)} {org.id.rjust(40)}"

        @builder.empty_cmd()
        def _do_list(self):
            '''list available orgs'''
            return self._list()

        @builder.empty_cmd()
        def _do_select(self, idx: int) -> Union[bool, CmdResponse]:
            '''change scope into org [idx]'''

            selected = self.get_thing_by_index(idx)

            return NewScopeResponse(OrgScope(Config(credentials=self.credentials,
                                   org=selected)))

        @builder.cmd(permissions=['admin:orgs:write', 'tenant:orgs:write'])
        def do_add(self, _arg):
            '''add new org'''
            org = OrgBuilder(credentials=self.credentials).from_user().build()

        @builder.cmd(permissions=['admin:orgs:delete', 'tenant:orgs:delete'])
        def do_del(self, idx):
            '''delete org [idx]'''
            selected: Organization = self.get_thing_by_index(
                self.arg_as_idx(idx))
            assert selected.id

            if Builder.get_yes_no(f"Really delete {selected.org_name}?", default_yes=False):
                self.client.org_delete(selected.id)
                print(f"Deleted {selected.org_name}")

        @builder.cmd(permissions=['admin:orgs:account', 'orgs:account'])
        def do_token(self, idx):
            '''get service account token for [idx]'''
            selected: Organization = self.get_thing_by_index(
                self.arg_as_idx(idx))
            assert selected.id

            print(self.client.svc_token(selected.id))

        @builder.cmd(permissions=['admin:orgs:read', 'orgs:my:read'])
        def do_info(self, idx: int):
            '''retrieve organization details'''
            selected = self.get_thing_by_index(self.arg_as_idx(idx))
            pprint(selected.as_dict())

        @builder.cmd(permissions=['admin:orgs:read', 'orgs:my:read'])
        def do_id(self, id: str) -> Union[bool, CmdResponse]:
            '''change scope into org id [id]'''

            for org in self.things:
                if org.id == id:
                    return NewScopeResponse(OrgScope(Config(credentials=self.credentials, org=org)))

            print(f"Unknown org id: {id}")
            return False

    return builder.build()(credentials)
