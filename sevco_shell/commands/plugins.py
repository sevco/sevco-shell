import colorama
from sevco_shell.builders.plugin import PluginBuilder
from sevco_shell.clients.plugin_repository.client import PluginClient
from sevco_shell.clients.plugin_repository.models import Plugin
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config


def PluginsCmd(config: Config, source_id: str):
    builder = CommandBuilder('plugins', config.credentials)

    @builder.from_cls()
    class _PluginsCmd(CommandWithList):
        '''Plugins - manage source plugins'''

        def __init__(self, config: Config, source_id: str):
            self.config = config
            super().__init__()

            self.source_id = source_id
            self.client = PluginClient(
                api_host=self.config.credentials.api_host, auth_token=self.config.credentials.auth_token, target_org=config.org.id)

            self.defaults = {plugin.os: plugin.id for plugin in self.client.list(
                source_id=source_id, default_only=True)}

        def get_things(self):
            plugins = [p for p in self.client.list(
                source_id=self.source_id) if p.enabled]
            return sorted(plugins, key=lambda x: x.last_updated_timestamp, reverse=True)

        def things_header(self):
            return [("Version", 20), ("OS", 20), ("Default", 7)]

        def format_thing(self, plugin: Plugin) -> str:
            version = plugin.display_version if plugin.display_version else plugin.version
            is_default = "●" if self.defaults.get(plugin.os) == plugin.id else ""

            return f"{version.rjust(20)} {plugin.os.value.rjust(20)} {colorama.Fore.RED}{is_default.center(7)}{colorama.Style.RESET_ALL}"

        @builder.empty_cmd()
        def _do_list(self):
            '''list available plugins'''
            return self._list()

        @builder.cmd(permissions=['admin:source:plugins:create'])
        def do_add(self, arg):
            '''add new source plugin'''
            PluginBuilder(self.config, self.source_id).from_user().build()

        @builder.cmd(permissions=['admin:source:plugins:update'])
        def do_default(self, idx):
            '''make plugin [idx] default'''
            selected: Plugin = self.get_thing_by_index(self.arg_as_idx(idx))

            self.client.set_default(selected.id)
            print("Default updated")

    return builder.build()(config, source_id)
