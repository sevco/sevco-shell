import json
import logging
from typing import List, Optional

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.source_audit.model import (PageinatedResponseV2,
                                                    SourceExecutionV2)

LOG = logging.getLogger(__name__)


class SourceAuditClient(SevcoClient):
    def list(self, audit_type: str, per_page: int = 100, page: int = 1, source_config_id: Optional[str] = None, execution_id: Optional[str] = None) -> List[SourceExecutionV2]:
        params = {
            "type": audit_type,
            "per_page": per_page,
            "page": page,
        }
        if execution_id:
            params['execution_id'] = execution_id
        if source_config_id:
            params['source_config_id'] = source_config_id

        resp = self.api_get("/v2/audit/source", params=params)

        paginated: PageinatedResponseV2 = PageinatedResponseV2.from_dict(
            json.loads(resp.text))

        return paginated.items

    def add(self, source_execution: SourceExecutionV2) -> SourceExecutionV2:
        resp = self.api_post(f"/v2/audit/source",
                             data=json.dumps(source_execution.as_dict()))

        return SourceExecutionV2.from_dict(json.loads(resp.text))

    def delete(self, audit_type: str, execution_id: str) -> None:
        resp = self.api_delete(f"/v2/audit/source",
                               params={"type": audit_type,
                                       "execution_id": execution_id})
