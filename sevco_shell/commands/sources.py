from sevco_shell.clients.scheduler.client import SchedulerServiceClient
from typing import Union

from sevco_shell.builders.source import (SourceBuilder, SourceScheduleBuilder,
                                         SourceSchemaBuilder)
from sevco_shell.builders.source_config import SourceConfigBuilder
from sevco_shell.clients.source_catalog.client import SourceCatalogClient
from sevco_shell.clients.source_catalog.models import Source
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config
from sevco_shell.scopes.scope import CmdResponse, NewScopeResponse, Scope
from sevco_shell.scopes.source import SourceScope


def SourcesCmd(config: Config) -> CommandWithList:
    builder = CommandBuilder('sources', config.credentials)

    @builder.from_cls()
    class _SourcesCmd(CommandWithList):
        '''Sources - work with available integration sources available in the source catalog.'''

        def __init__(self, config: Config):
            self.config = config

            super().__init__()

            self.client = SourceCatalogClient(
                api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
            self.scheduler_client = SchedulerServiceClient(
                api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)

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

        def get_things(self):
            return self.client.list()

        def things_header(self):
            return [("Source", 40)]

        def format_thing(self, source: Source) -> str:
            return source.display_name.rjust(40)

        @builder.empty_cmd()
        def _do_list(self):
            '''list available sources'''
            return self._list()

        @builder.empty_cmd()
        def _do_select(self, idx: int) -> CmdResponse:
            '''change scope into source [idx]'''
            selected = self.get_thing_by_index(idx)

            return NewScopeResponse(SourceScope(self.config, selected))

        @builder.cmd(permissions=['admin:source:config:write', 'source:config:write'])
        def do_config(self, idx):
            '''configure source [idx]'''
            selected: Source = self.get_thing_by_index(self.arg_as_idx(idx))

            source_config = SourceConfigBuilder(self.config, selected.id).from_user().build()
            if source_config:
                try:
                    self.scheduler_client.execute(source_config_id=source_config.id)
                except Exception as e:
                    print(f"Unable to schedule immediate execution: {e}")

        @builder.cmd(permissions=['admin:source:create'])
        def do_add(self, _arg):
            '''add new source'''
            print("Source Configuration")
            source = SourceBuilder(config=self.config).from_user().build()
            if source:
                print("Source Schema Configuration")
                schema = SourceSchemaBuilder(config=self.config,
                                             source_id=source.id).from_user().build()
                if schema:
                    print("Source Schedule")
                    SourceScheduleBuilder(config=self.config,
                                          source_id=source.id).from_user().build()

    return builder.build()(config)
