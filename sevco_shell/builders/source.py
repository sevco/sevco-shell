from typing import Optional

from sevco_shell.builders.builder import Builder
from sevco_shell.clients.scheduler.client import SchedulerServiceClient
from sevco_shell.clients.scheduler.models import DataSourceSchedule
from sevco_shell.clients.schema.client import SchemaClient, SourceSchemaClient
from sevco_shell.clients.schema.models import (SourceSchemaByName,
                                               SourceSchemaByNameArray,
                                               SourceSchemaInfo,
                                               SourceSchemaRunnerRequirements)
from sevco_shell.clients.source_catalog.client import SourceCatalogClient
from sevco_shell.clients.source_catalog.models import Source, SourceInput
from sevco_shell.config import Config


class SourceBuilder(Builder):
    def __init__(self, config: Config):
        self.client = SourceCatalogClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.source_input = None
        self.source = None

    def from_user(self) -> 'SourceBuilder':
        try:
            self.source_input = self._from_user()
        except KeyboardInterrupt:
            print()

        return self

    def _from_user(self) -> SourceInput:
        source_type = self.get_input("Source Type")  # TODO: check format
        display_name = self.get_input("Display Name")
        is_cloud = self.get_yes_no("Cloud")
        is_public = self.get_yes_no("Public")

        return SourceInput(
            source_type, is_cloud, is_public, display_name)

    def build(self) -> Optional[Source]:
        if self.source_input:
            source = self.client.create(source_input=self.source_input)
            print(f"Created source {source.id}")
            return source

        return None


class SourceSchemaBuilder(Builder):
    def __init__(self, config: Config, source_id: str):
        self.schemas_client = SchemaClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.client = SourceSchemaClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.source_id = source_id

        self.auth_schemas = [s['title']
                             for s in self.schemas_client.list("auth")]
        self.connect_schemas = [s['title']
                                for s in self.schemas_client.list("connect")]
        self.settings_schemas = [s['title']
                                 for s in self.schemas_client.list("settings")]

        self.schemas = None

    def from_user(self) -> 'SourceSchemaBuilder':
        try:
            self.schemas = self._from_user()
        except KeyboardInterrupt:
            print()

        return self

    def _from_user(self) -> SourceSchemaByName:
        schemas = self._build_schema()

        return schemas

    def _build_schema(self) -> SourceSchemaByName:
        description = self.get_input("Description")
        runner_required = self.get_yes_no("Runner Required", False)
        runner_configurable = self.get_yes_no("Runner Configurable", False)

        connect = self.get_one_of("Connect Schema", self.connect_schemas)
        auth = self.get_one_of("Auth Schema", self.auth_schemas)
        settings = self.get_one_of("Settings Schema", self.settings_schemas)

        return SourceSchemaByName(info=SourceSchemaInfo(description=description,
                                                        runner_requirements=SourceSchemaRunnerRequirements(required=runner_required,
                                                                                                           configurable=runner_configurable)),
                                  connect=connect,
                                  auth=auth,
                                  settings=settings)

    def build(self) -> Optional[SourceSchemaByName]:
        if self.schemas:
            all_schemas = self.client.get(self.source_id)
            by_name = [SourceSchemaByName(info=schema.info,
                                          auth=schema.auth['title'],
                                          connect=schema.connect['title'],
                                          settings=schema.settings['title']) for schema in all_schemas]
            by_name.append(self.schemas)

            schemas = self.client.add(
                self.source_id, source_schemas=SourceSchemaByNameArray(types=by_name))
            print("Schemas added")

            return self.schemas

        return None


class SourceScheduleBuilder(Builder):
    def __init__(self, config: Config, source_id: str):
        self.client = SchedulerServiceClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.source_id = source_id
        self.schedule = None

    def from_user(self) -> 'SourceScheduleBuilder':
        try:
            self.schedule = self._from_user()
        except KeyboardInterrupt:
            print()

        return self

    def _from_user(self) -> DataSourceSchedule:
        schedule_config = self.get_input("Schedule", required=True)

        return DataSourceSchedule(source_id=self.source_id,
                                  schedule_config=schedule_config)

    def build(self, update: bool = False) -> Optional[DataSourceSchedule]:
        if self.schedule:
            if update:
                schedule = self.client.update(schedule=self.schedule)
                print("Schedule set")
            else:
                schedule = self.client.add(schedule=self.schedule)
                print("Schedule set")
            return schedule

        return None
