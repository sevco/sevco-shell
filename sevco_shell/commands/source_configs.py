from datetime import datetime
from pprint import pprint
from typing import Dict, Optional

from sevco_shell.builders.builder import Builder
from sevco_shell.clients.source_audit.client import SourceAuditClient
from sevco_shell.clients.source_catalog.client import SourceCatalogClient
from sevco_shell.clients.source_catalog.models import Source
from sevco_shell.clients.source_config.client import SourceConfigClient
from sevco_shell.clients.source_config.model import SourceConfig
from sevco_shell.clients.source_oauth.client import SourceOAuthClient
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config


def SourceConfigsCmd(config: Config, source: Optional[Source] = None):
    builder = CommandBuilder('configs', config.credentials)

    @builder.from_cls()
    class SourceConfigsCmd(CommandWithList):
        '''Configs - manage source configs'''

        def __init__(self, config: Config, source: Optional[Source] = None):
            self.config = config
            super().__init__()

            self.source = source
            self.client = SourceConfigClient(
                api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)

            catalog_client = SourceCatalogClient(
                api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
            self.sources_by_id = {self.source.id: self.source} if self.source else {
                source.id: source for source in catalog_client.list()}

        def get_things(self):
            def get_timestamp(x: SourceConfig) -> datetime:
                assert x.last_updated_timestamp
                return x.last_updated_timestamp

            return sorted(self.client.list(source_id=self.source.id if self.source else None), key=get_timestamp, reverse=True)

        def things_header(self):
            return [("ID", 36), ("Source", 20)]

        def format_thing(self, config: SourceConfig) -> str:
            source = self.sources_by_id.get(config.source_id)
            return f"{config.id.rjust(36)} {source.display_name.rjust(20) if source else 'UNKNOWN'.rjust(20)}"

        @builder.empty_cmd()
        def _do_list(self):
            '''list source configs'''
            return self._list()

        @builder.cmd(permissions=['admin:source:config:read', 'source:config:read'])
        def do_info(self, idx):
            '''retrieve details for config [idx]'''

            selected: SourceConfig = self.get_thing_by_index(
                self.arg_as_idx(idx))

            pprint(selected.as_dict())

        @builder.cmd(permissions=['admin:source:audit:read', 'source:audit:read'])
        def do_audit(self, idx):
            '''retrieve last 10 execution audit logs for config [idx]'''

            selected: SourceConfig = self.get_thing_by_index(
                self.arg_as_idx(idx))

            client = SourceAuditClient(
                api_host=self.config.credentials.api_host, auth_token=self.config.credentials.auth_token, target_org=self.config.org.id)

            for audit in client.list("execution", source_config_id=selected.id, per_page=10):
                pprint(audit.as_dict())

        @builder.cmd(permissions=['admin:source:oauth:read', 'source:oauth:read'])
        def do_oauth(self, idx):
            '''initiate OAuth2 workflow for config [idx]'''

            selected: SourceConfig = self.get_thing_by_index(
                self.arg_as_idx(idx))
            assert selected.id

            if selected.auth.schema != 'oauth2':
                raise Exception("Not an OAuth2 config")

            client = SourceOAuthClient(
                api_host=self.config.credentials.api_host, auth_token=self.config.credentials.auth_token, target_org=self.config.org.id)

            url = client.initiate(source_config_id=selected.id)
            print("Browse to the following to initiate the OAuth workflow:")
            print(url)

        @builder.cmd(permissions=['admin:source:config:delete', 'source:config:delete'])
        def do_del(self, idx):
            '''delete config [idx]'''
            selected: SourceConfig = self.get_thing_by_index(
                self.arg_as_idx(idx))
            assert selected.id

            if Builder.get_yes_no(f"Really delete {selected.id}?", default_yes=False):
                self.client.delete(selected.id)
                print(f"Deleted {selected.id}")

    return builder.build()(config, source)
