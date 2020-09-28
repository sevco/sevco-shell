from sevco_shell.config.credentials import ApiCredentials
from sevco_shell.commands.orgs import OrgsCmd
from sevco_shell.scopes.scope import Scope


class SvScope(Scope):
    def __init__(self, credentials: ApiCredentials):
        super().__init__('svsh')
        self.credentials = credentials

        self.register_cmd('orgs', OrgsCmd(credentials=credentials))
