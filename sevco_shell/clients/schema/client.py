import json
from typing import Any, Dict, List

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.schema.models import (SourceSchemaByNameArray,
                                               SourceSchemas)


class SchemaClient(SevcoClient):
    def list(self, category: str) -> List[Dict[str, Any]]:
        resp = self.api_get(f"/v1/schema/{category}")

        return json.loads(resp.text)  # type: ignore

    def get(self, category: str, schema_type: str) -> Dict[str, Any]:
        resp = self.api_get("/v1/schema/{category}/{schema_type}")

        return json.loads(resp.text)


class SourceSchemaClient(SevcoClient):
    def get(self, source_id: str) -> List[SourceSchemas]:
        resp = self.api_get(f"/v1/integration/source/{source_id}/schema")

        return [SourceSchemas.from_dict(d) for d in json.loads(resp.text)]

    def delete(self, source_id: str) -> None:
        self.api_delete(f"/v1/integration/source/{source_id}/schema")

    def add(self, source_id: str, source_schemas: SourceSchemaByNameArray) -> SourceSchemaByNameArray:
        resp = self.api_post(f"/v1/integration/source/{source_id}/schema",
                             data=json.dumps(source_schemas.as_dict()))

        return SourceSchemaByNameArray.from_dict(json.loads(resp.text))

    def update(self, source_id: str, source_schemas: SourceSchemaByNameArray) -> SourceSchemaByNameArray:
        resp = self.api_put(f"/v1/integration/source/{source_id}/schema",
                            data=json.dumps(source_schemas.as_dict()))

        return SourceSchemaByNameArray.from_dict(json.loads(resp.text))
