from dataclasses import dataclass
import datetime
from sevco_shell.clients.models import with_dict
from typing import Optional


@dataclass
class SourceInput(with_dict):
    source_type: str
    is_cloud: bool
    is_public: bool
    display_name: str
    icon: Optional[str]=None


@dataclass
class Source(with_dict):
    id: str
    source_type: str
    is_cloud: bool
    owner: str
    is_public: bool
    display_name: str
    created_timestamp: datetime.datetime
    last_updated_timestamp: datetime.datetime
    icon: Optional[str]=None

    def to_input(self) -> SourceInput:
        return SourceInput(source_type=self.source_type,
                           is_cloud=self.is_cloud,
                           is_public=self.is_public,
                           display_name=self.display_name,
                           icon=self.icon)
