import json
from typing import List, Optional

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.plugin_repository.models import Plugin, PluginInput

PLUGIN_URL_ROOT = "/v1/integration/source/plugin"


class PluginClient(SevcoClient):
    def create(self, plugin_input: PluginInput) -> Plugin:
        if not plugin_input.binary_url and not plugin_input.binary:
            raise Exception("Must provide 'binary_url' or 'binary'")

        resp = self.api_post(
            PLUGIN_URL_ROOT,
            data=json.dumps(plugin_input.as_dict()),
            files=plugin_input.binary
        )

        return Plugin.from_dict(json.loads(resp.text))

    def list(self, source_id: Optional[str]=None, default_only: bool=False, os: Optional[str]=None) -> List[Plugin]:
        query_params = {}
        if default_only:
            query_params["default_only"] = str(default_only)
        if os:
            query_params["os"] = os
        if source_id:
            query_params["source_id"] = source_id

        resp = self.api_get(
            PLUGIN_URL_ROOT,
            params=query_params
        )

        return [Plugin.from_dict(d) for d in json.loads(resp.text)]

    def get(self, plugin_id: str) -> Plugin:
        resp = self.api_get(
            f"{PLUGIN_URL_ROOT}/{plugin_id}"
        )

        return Plugin.from_dict(json.loads(resp.text))

    def update(self, plugin_id: str, plugin_input: PluginInput) -> Plugin:
        resp = self.api_put(
            f"{PLUGIN_URL_ROOT}/{plugin_id}",
            data=json.dumps(plugin_input.as_dict())
        )

        return Plugin.from_dict(json.loads(resp.text))

    def delete(self, plugin_id: str) -> None:
        resp = self.api_delete(
            f"{PLUGIN_URL_ROOT}/{plugin_id}"
        )

    def set_default(self, plugin_id: str) -> None:
        resp = self.api_put(
            f"{PLUGIN_URL_ROOT}/{plugin_id}/default"
        )

    def download(self, plugin_id: str) -> str:
        resp = self.api_get(
            f"{PLUGIN_URL_ROOT}/{plugin_id}/download"
        )

        return resp.json()['url']