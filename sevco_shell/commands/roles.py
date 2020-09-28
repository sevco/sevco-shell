import colorama
from pprint import pprint
from sevco_shell.builders.builder import Builder
from sevco_shell.builders.tenant import AddUserBuilder

from sevco_shell.clients.tenant.client import TenantClient
from sevco_shell.clients.tenant.models import Role, User
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config


def RolesCmd(config: Config, user: User):
    builder = CommandBuilder('roles', credentials=config.credentials)

    @builder.from_cls()
    class _RolesCmd(CommandWithList):
        '''Roles - manage and interact with roles'''

        def __init__(self, config: Config, user: User):
            super().__init__()
            self.config = config
            self.user = user
            self.client = TenantClient(
                config.credentials.api_host, config.credentials.auth_token, target_org=config.org.id)

        def get_things(self):
            return sorted(self.client.roles(), key=lambda x: x.name)

        def things_header(self):
            return [("Name", 20), ("Description", 40), ("Active", 6)]

        def format_thing(self, role: Role) -> str:
            enabled = "●" if role.name in self.user.roles else ''
            return f"{role.name.rjust(20)} {role.description.rjust(40)} {colorama.Fore.RED}{enabled.center(6)}{colorama.Style.RESET_ALL}"

        @builder.empty_cmd()
        def _do_list(self):
            '''list org roles'''
            return self._list()

        @builder.cmd(permissions=['admin:roles:read', 'tenant:roles:read', 'roles:read'])
        def do_info(self, idx):
            '''show role details'''
            selected: Role = self.get_thing_by_index(self.arg_as_idx(idx))

            pprint(selected.as_dict())

        @builder.cmd(permissions=['org:user:write'])
        def do_add(self, idx):
            '''add role to user'''
            selected: Role = self.get_thing_by_index(self.arg_as_idx(idx))
            self.client.user_add_role(self.user.email, selected.name)
            print(f"Added {selected.name}")
            self.user = self.client.get_user(self.user.email)

        @builder.cmd(permissions=['org:user:write'])
        def do_del(self, idx):
            '''remove role from user'''
            selected: Role = self.get_thing_by_index(self.arg_as_idx(idx))
            self.client.user_delete_role(self.user.email, selected.name)
            print(f"Removed {selected.name}")
            self.user = self.client.get_user(self.user.email)

    return builder.build()(config, user)
