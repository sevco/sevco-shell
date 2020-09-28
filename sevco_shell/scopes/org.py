from sevco_shell.commands.source_configs import SourceConfigsCmd
from sevco_shell.commands.runners import RunnersCmd
from sevco_shell.config import Config
from sevco_shell.commands.sources import SourcesCmd
from sevco_shell.commands.users import UsersCmd
from sevco_shell.scopes.scope import Scope


class OrgScope(Scope):
    def __init__(self, config: Config):
        self.config = config
        super().__init__(config.org.org_name)
        self.register_cmd('sources', SourcesCmd(config))
        self.register_cmd('runners', RunnersCmd(config))
        self.register_cmd('configs', SourceConfigsCmd(config))
        self.register_cmd('users', UsersCmd(config))
