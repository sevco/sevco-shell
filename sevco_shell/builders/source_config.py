from typing import Any, Dict, Optional

from sevco_shell.builders.builder import Builder
from sevco_shell.clients.schema.client import SourceSchemaClient
from sevco_shell.clients.source_config.client import SourceConfigClient
from sevco_shell.clients.source_config.model import (SchemaInstance,
                                                     SourceConfig)
from sevco_shell.config import Config


class SourceConfigBuilder(Builder):
    def __init__(self, config: Config, source_id: Optional[str]):
        self.client = SourceConfigClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.schema_client = SourceSchemaClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.source_id = source_id
        self.config = None

    def from_user(self) -> 'SourceConfigBuilder':
        try:
            self.config = self._from_user()
        except KeyboardInterrupt:
            print()

        return self

    def _from_user(self) -> SourceConfig:
        '''Create new config for source: ADD SOURCE_ID'''
        if not self.source_id:
            self.source_id = self.get_input("Source ID:", required=True)

        schemas = self.schema_client.get(self.source_id)
        schema_desc = schemas[0].info.description

        if len(schemas) > 1:
            schema_desc = self.get_one_of(
                "Choose schema", [schema.info.description for schema in schemas])

        schema = next(
            iter(schema for schema in schemas if schema.info.description == schema_desc))

        print(f"Configuration: {schema.info.description}")

        connect_config = self._collect_config(schema.connect)
        auth_config = self._collect_config(schema.auth)
        settings_config = self._collect_config(schema.settings)

        runner_id = None
        if schema.info.runner_requirements.configurable:
            if schema.info.runner_requirements.required:
                runner_id = input("Runner ID (required): ")
                while runner_id == "":
                    runner_id = input("Runner ID (required): ")
            else:
                runner_id = input("Runner ID (<RETURN> to skip): ")
                if not runner_id:
                    runner_id = None

        enabled = self.get_yes_no("Enabled")

        return SourceConfig(source_id=self.source_id,
                            enabled=enabled,
                            runner_id=runner_id,
                            connect=connect_config if connect_config else None,
                            auth=auth_config if auth_config else None,
                            settings=settings_config if settings_config else None)

    def build(self) -> Optional[SourceConfig]:
        if self.config:
            config = self.client.add(self.config)
            print(f"Created source config: {config.id}")
            return config

        return None

    def _collect_config(self, schema: Dict[str, Any]) -> Optional[SchemaInstance]:
        if schema['title'] in ['empty', 'oauth2']:
            return None

        config = {}

        for field, prop in schema['properties'].items():
            prompt = prop['description']

            if prop.get('writeOnly', False):
                v = self.get_password(prompt)
            else:
                required = field in schema["required"]
                v = self.get_input(prompt, required=required)

            config[field] = v

        return SchemaInstance(schema=schema['title'], instance=config)
