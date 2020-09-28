import json
import logging
from typing import List, Optional

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.source_config.model import SourceConfig

LOG = logging.getLogger(__name__)


class SourceConfigClient(SevcoClient):
    def get(self, id: str, oauth_refresh=True, **kwargs) -> SourceConfig:
        resp = self.api_get(f"/v1/integration/source/config/{id}", params={
                            "oauth_refresh": "true" if oauth_refresh else "false"}, **kwargs)

        return SourceConfig.from_dict(json.loads(resp.text))

    def list(self, source_id: Optional[str] = None, is_enabled: Optional[bool] = None, oauth_refresh=True, **kwargs) -> List[SourceConfig]:
        params = {"oauth_refresh": "true" if oauth_refresh else "false"}

        if source_id:
            params['source_id'] = source_id
        if is_enabled is not None:
            params['enabled'] = "true" if is_enabled else "false"

        resp = self.api_get("/v1/integration/source/config",
                            params=params,
                            **kwargs)

        return [SourceConfig.from_dict(d) for d in json.loads(resp.text)]

    def add(self, source_config: SourceConfig, **kwargs) -> SourceConfig:
        resp = self.api_post("/v1/integration/source/config",
                             data=json.dumps(source_config.as_dict()),
                             **kwargs)

        return SourceConfig.from_dict(json.loads(resp.text))

    def delete(self, id: str, **kwargs) -> None:
        self.api_delete(f"/v1/integration/source/config/{id}", **kwargs)

    def update(self, source_config: SourceConfig, **kwargs) -> SourceConfig:
        resp = self.api_put(f"/v1/integration/source/config/{source_config.id}",
                            data=json.dumps(source_config.as_dict()),
                            **kwargs)

        return SourceConfig.from_dict(json.loads(resp.text))
