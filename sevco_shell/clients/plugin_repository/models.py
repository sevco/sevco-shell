import datetime
from dataclasses import dataclass
from typing import Dict, Optional

from sevco_shell.clients.models import OperatingSystem, with_dict


@dataclass
class PluginInput(with_dict):
    source_id: str
    os: OperatingSystem
    enabled: bool
    display_version: Optional[str] = ""
    release_notes: Optional[str] = ""
    binary_url: Optional[str] = None
    binary: Optional[Dict] = None


@dataclass
class Plugin(with_dict):
    id: str
    version: str
    display_version: str
    release_notes: str
    source_id: str
    signature: str
    os: OperatingSystem
    enabled: bool
    created_timestamp: datetime.datetime
    last_updated_timestamp: datetime.datetime