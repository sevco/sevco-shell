from sevco_shell.clients.tenant.models import User
from sevco_shell.config import Config
from sevco_shell.commands.roles import RolesCmd
from sevco_shell.scopes.scope import Scope


class UserScope(Scope):
    def __init__(self, config: Config, user: User):
        self.config = config
        self.user = user
        super().__init__(self.user.name)

        self.register_cmd('roles', RolesCmd(config, user))
