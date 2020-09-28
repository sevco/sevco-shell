import datetime
from dataclasses import dataclass
from typing import List, Optional

from sevco_shell.clients.models import with_dict


@dataclass
class SourceExecution(with_dict):
    source_config_id: str
    runner_id: str
    timestamp: datetime.datetime
    exec_status: int
    reason: str
    runner_version: str
    plugin_id: str
    execution_id: str
    org_id: Optional[str] = None


@dataclass
class PageinationDefinition(with_dict):
    page: int
    per_page: int

    @classmethod
    def make_from_items(cls, items: List, limit: int, offset: int):
        return cls(
            per_page=limit,
            page=max(int((offset + len(items)) / limit), 1)
        )


@dataclass
class PageinatedResponse(with_dict):
    items: List[SourceExecution]
    pagination: PageinationDefinition
