import json
import logging
from typing import Dict

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.source_config.model import SourceConfig
from sevco_shell.clients.source_oauth.model import SourceOAuthSettings

LOG = logging.getLogger(__name__)


class SourceOAuthClient(SevcoClient):
    def get(self, source_id: str, **kwargs) -> SourceOAuthSettings:
        resp = self.api_get(
            f"/v1/integration/source/{source_id}/oauth", **kwargs)

        return SourceOAuthSettings.from_dict(json.loads(resp.text))

    def add(self, source_oauth_settings: SourceOAuthSettings, **kwargs) -> SourceOAuthSettings:
        resp = self.api_post(f"/v1/integration/source/{source_oauth_settings.source_id}/oauth",
                             data=json.dumps(source_oauth_settings.as_dict()),
                             **kwargs)

        return SourceOAuthSettings.from_dict(json.loads(resp.text))

    def update(self, source_oauth_settings: SourceOAuthSettings, **kwargs) -> SourceOAuthSettings:
        resp = self.api_put(f"/v1/integration/source/{source_oauth_settings.source_id}/oauth",
                            data=json.dumps(source_oauth_settings.as_dict()),
                            **kwargs)

        return SourceOAuthSettings.from_dict(json.loads(resp.text))

    def delete(self, source_id: str, **kwargs) -> None:
        resp = self.api_delete(
            f"/v1/integration/source/{source_id}/oauth", **kwargs)

    def initiate(self, source_config_id: str, **kwargs) -> str:
        resp = self.api_get(
            f"/v1/integration/source/config/{source_config_id}/oauth/initiate", **kwargs)

        return resp.json()['url']

    def refresh(self, source_config_id: str, **kwargs) -> SourceConfig:
        resp = self.api_put(
            f"/v1/integration/source/config/{source_config_id}/oauth/refresh", **kwargs)

        return SourceConfig.from_dict(json.loads(resp.text))

    def revoke(self, source_config_id: str, **kwargs) -> Dict:
        resp = self.api_delete(
            f"/v1/integration/source/config/{source_config_id}/oauth/revoke", **kwargs)

        return resp.json()
