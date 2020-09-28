from sevco_shell.clients.source_catalog.models import Source
from sevco_shell.commands.plugins import PluginsCmd
from sevco_shell.commands.schedule import ScheduleCmd
from sevco_shell.commands.schemas import SchemasCmd
from sevco_shell.commands.source_configs import SourceConfigsCmd
from sevco_shell.config import Config
from sevco_shell.scopes.scope import Scope


class SourceScope(Scope):
    def __init__(self, config: Config, source: Source):
        self.config = config
        super().__init__(source.display_name)

        self.configs = []
        self.source = source
        self.register_cmd('plugins', PluginsCmd(self.config, self.source.id))
        self.register_cmd('configs', SourceConfigsCmd(self.config, self.source))
        self.register_cmd('schemas', SchemasCmd(self.config, self.source))
        self.register_cmd('schedule', ScheduleCmd(self.config, self.source))
