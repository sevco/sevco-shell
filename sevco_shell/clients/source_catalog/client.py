import json
from typing import Dict, List

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.source_catalog.models import Source, SourceInput

SOURCE_CATALOG_URL_ROOT = "/v1/integration/source"


class SourceCatalogClient(SevcoClient):
    def healthcheck(self) -> Dict:
        resp = self.api_get(
            "/v1/healthcheck/source-catalog-service"
        )

        return resp.json()

    def create(self, source_input: SourceInput) -> Source:
        resp = self.api_post(
            SOURCE_CATALOG_URL_ROOT,
            data=json.dumps(source_input.as_dict())
        )

        return Source.from_dict(json.loads(resp.text))

    def update(self, source_id: str, source_input: SourceInput) -> Source:
        resp = self.api_put(
            f"{SOURCE_CATALOG_URL_ROOT}/{source_id}",
            data=json.dumps(source_input.as_dict())
        )

        return Source.from_dict(json.loads(resp.text))

    def list(self) -> List[Source]:
        resp = self.api_get(
            SOURCE_CATALOG_URL_ROOT
        )

        return [Source.from_dict(d) for d in json.loads(resp.text)]

    def get(self, source_id: str) -> Source:
        resp = self.api_get(
            f"{SOURCE_CATALOG_URL_ROOT}/{source_id}"
        )

        return Source.from_dict(json.loads(resp.text))

    def delete(self, source_id: str) -> None:
        self.api_delete(
            f"{SOURCE_CATALOG_URL_ROOT}/{source_id}"
        )
