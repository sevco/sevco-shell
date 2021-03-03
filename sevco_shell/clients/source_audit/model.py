import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional

from sevco_shell.clients.models import with_dict


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
class RunnerInfo(with_dict):
    id: str
    version: str


@dataclass
class ExecutionInfo(with_dict):
    id: str
    source_config_id: str
    plugin_id: str
    queued_timestamp: datetime.datetime
    received_timestamp: datetime.datetime
    completed_timestamp: datetime.datetime
    exit_code: int
    stderr: str


@dataclass
class ResultInfo(with_dict):
    status_code: str
    message: str
    count: int


@dataclass
class SourceExecutionV2(with_dict):
    org_id: str
    runner: RunnerInfo
    execution: ExecutionInfo
    result: ResultInfo


@dataclass
class PageinatedResponseV2(with_dict):
    items: List[SourceExecutionV2]
    pagination: PageinationDefinition


@dataclass
class SourceExecutionsLatestResponseV2(with_dict):
    source_configs: Dict[str, SourceExecutionV2]