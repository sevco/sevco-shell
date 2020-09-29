from pprint import pprint

from sevco_shell.builders.source import SourceSchemaBuilder
from sevco_shell.clients.schema.client import SourceSchemaClient
from sevco_shell.clients.schema.models import (SourceSchemaByName,
                                               SourceSchemaByNameArray,
                                               SourceSchemas)
from sevco_shell.clients.source_catalog.models import Source
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config


def SchemasCmd(config: Config, source: Source):
    builder = CommandBuilder('schemas', config.credentials)

    @builder.from_cls()
    class _SchemasCmd(CommandWithList):
        '''Schemas - view and manage source configuration schemas'''

        def __init__(self, config: Config, source: Source):
            self.config = config
            super().__init__()

            self.source = source
            self.schema_client = SourceSchemaClient(
                api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)

        def get_things(self):
            return self.schema_client.get(self.source.id)

        def things_header(self):
            return [("Schema", 20)]

        def format_thing(self, schemas: SourceSchemas) -> str:
            return schemas.info.description.rjust(20)

        @builder.empty_cmd()
        def _do_list(self):
            '''list source schemas'''
            return self._list()

        @builder.cmd(permissions=['admin:schema:read', 'schema:read'])
        def do_info(self, idx):
            '''retreive schema details'''
            selected: SourceSchemas = self.get_thing_by_index(self.arg_as_idx(idx))
            pprint(selected.as_dict())

        @builder.cmd(permissions=['admin:source:update'])
        def do_del(self, idx):
            '''delete source schema'''
            selected: SourceSchemas = self.get_thing_by_index(self.arg_as_idx(idx))

            all_schemas = self.schema_client.get(self.source.id)
            updated = [SourceSchemaByName(info=schema.info,
                                          auth=schema.auth['title'],
                                          connect=schema.connect['title'],
                                          settings=schema.settings['title']) for schema in all_schemas if schema.info.description != selected.info.description]
            self.schema_client.update(
                self.source.id, SourceSchemaByNameArray(types=updated))

        @builder.cmd(permissions=['admin:source:update'])
        def do_add(self, arg):
            '''add source schemas'''
            SourceSchemaBuilder(config=self.config,
                                source_id=self.source.id).from_user().build()

    return builder.build()(config, source)
