from enum import Enum
from typing import List, Optional

from sevco_shell.builders.builder import Builder
from sevco_shell.clients.models import OperatingSystem
from sevco_shell.clients.plugin_repository.client import PluginClient
from sevco_shell.clients.plugin_repository.models import Plugin, PluginInput
from sevco_shell.config import Config


class OperatingSystemFiendlyName(Enum):
    WINDOWS_AMD64 = 'windows'
    DARWIN_AMD64 = 'darwin'
    LINUX_AMD64 = 'linux'

    @classmethod
    def keys(cls) -> List[str]:
        return list(cls.__dict__.get('_value2member_map_').keys())


class PluginBuilder(Builder):
    def __init__(self, config: Config, source_id=str):
        self.client = PluginClient(
            api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
        self.source_id = source_id
        self.plugin_input = None

    def from_user(self) -> 'PluginBuilder':
        try:
            self.plugin_input = self._from_user()
        except KeyboardInterrupt:
            print()

        return self

    def _from_user(self) -> PluginInput:
        display_version = self.get_input("Display Version", required=False)
        os = OperatingSystem(OperatingSystemFiendlyName(self.get_one_of(
            "OS", OperatingSystemFiendlyName.keys())).name)
        enabled = self.get_yes_no("Enabled")
        default = self.get_yes_no("Make default")
        binary_url = self.get_input("Binary URL")

        return PluginInput(source_id=self.source_id,
                           display_version=display_version,
                           os=os,
                           enabled=enabled,
                           default=default,
                           binary_url=binary_url)

    def build(self) -> Optional[Plugin]:
        if self.plugin_input:
            plugin = self.client.create(plugin_input=self.plugin_input)
            print(f"Plugin created: {plugin.id}")
            return plugin

        return None
