from pprint import pprint
from sevco_shell.scopes.user import UserScope
from sevco_shell.scopes.scope import CmdResponse, NewScopeResponse
from typing import Union
from sevco_shell.builders.builder import Builder
from sevco_shell.builders.tenant import AddUserBuilder

from sevco_shell.clients.tenant.client import TenantClient
from sevco_shell.clients.tenant.models import User
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config


def UsersCmd(config: Config):
    builder = CommandBuilder('users', credentials=config.credentials)

    @builder.from_cls()
    class _UsersCmd(CommandWithList):
        '''Users - manage and interact with users'''

        def __init__(self, config: Config):
            super().__init__()
            self.config = config
            self.client = TenantClient(
                config.credentials.api_host, config.credentials.auth_token, target_org=config.org.id)

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

        @builder.empty_cmd()
        def _do_select(self, idx: int) -> CmdResponse:
            '''change scope into user [idx]'''

            selected = self.get_thing_by_index(idx)

            return NewScopeResponse(UserScope(self.config, selected))

        def get_things(self):
            return sorted(self.client.list_users(), key=lambda x: x.name)

        def things_header(self):
            return [("Name", 20), ("Email", 30)]

        def format_thing(self, user: User) -> str:
            return f"{user.nickname.rjust(20)} {user.email.rjust(30)}"

        @builder.empty_cmd()
        def _do_list(self):
            '''list org users'''
            return self._list()

        @builder.cmd(permissions=['org:user:read'])
        def do_info(self, idx):
            '''show user details'''
            selected: User = self.get_thing_by_index(self.arg_as_idx(idx))

            pprint(selected.as_dict())

        @builder.cmd(permissions=['org:user:write'])
        def do_add(self, _arg):
            '''add user to org'''
            AddUserBuilder(self.config).from_user().build()

        @builder.cmd(permissions=['org:user:delete'])
        def do_del(self, idx):
            '''remove user from org'''
            selected: User = self.get_thing_by_index(self.arg_as_idx(idx))
            if Builder.get_yes_no(f"Really remove user from {self.config.org.org_name}?", default_yes=False):
                self.client.delete_user(selected.email)

    return builder.build()(config)
