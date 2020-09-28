import json
import logging
from typing import List, Optional

import requests

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.source_audit.model import (PageinatedResponse,
                                                    SourceExecution)

LOG = logging.getLogger(__name__)


class SourceAuditClient(SevcoClient):
    def list(self, audit_type: str, per_page: int = 100, page: int = 1, source_config_id: Optional[str] = None, execution_id: Optional[str] = None) -> List[SourceExecution]:
        params = {
            "type": audit_type,
            "per_page": per_page,
            "page": page,
        }
        if execution_id:
            params['execution_id'] = execution_id
        if source_config_id:
            params['source_config_id'] = source_config_id

        resp = self.api_get("/v1/audit/source", params=params)

        paginated: PageinatedResponse = PageinatedResponse.from_dict(
            json.loads(resp.text))

        return paginated.items

    def add(self, source_execution: SourceExecution) -> SourceExecution:
        resp = self.api_post(f"/v1/audit/source",
                             data=json.dumps(source_execution.as_dict()))

        return SourceExecution.from_dict(json.loads(resp.text))

    def delete(self, audit_type: str, execution_id: str) -> None:
        resp = self.api_delete(f"/v1/audit/source",
                               params={"type": audit_type,
                                       "execution_id": execution_id})
