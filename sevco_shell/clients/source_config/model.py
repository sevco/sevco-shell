import datetime
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sevco_shell.clients.models import with_dict


@dataclass
class SchemaInstance(with_dict):
    schema: str
    instance: Dict[str, Any]


@dataclass
class SourceConfig(with_dict):
    source_id: str
    enabled: bool
    org_id: Optional[str] = None
    id: Optional[str] = None
    plugin_id: Optional[str] = None
    runner_id: Optional[str] = None
    connect: Optional[SchemaInstance] = None
    auth: Optional[SchemaInstance] = None
    settings: Optional[SchemaInstance] = None
    last_updated_timestamp: Optional[datetime.datetime] = None
    created_timestamp: Optional[datetime.datetime] = None
