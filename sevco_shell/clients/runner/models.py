import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from sevco_shell.clients.models import OperatingSystem, with_dict


def get_uuid() -> str:
    return str(uuid.uuid4())


@dataclass
class Runner(with_dict):
    org_id: str
    os: OperatingSystem
    runner_id: str = field(default_factory=get_uuid)
    version: Optional[str] = field(default=None)
    hostname: Optional[str] = field(default=None)
    display_name: Optional[str] = field(default=None)
    registration_time: datetime = field(default_factory=datetime.utcnow)
    last_checkin_time: Optional[datetime] = field(default=None)

    def get_queue_name(self, prefix: str) -> str:
        # Todo - get this sevco org_id from somewhere
        if self.org_id == '00000000-0000-0000-0000-000000000000':
            return f'{prefix}-runner-global'
        return f'{prefix}-runner-{self.runner_id}'


@dataclass
class AWSCredentials(with_dict):
    expiration: datetime
    access_key_id: str
    secret_key_id: str
    session_token: str


@dataclass
class RunnerConfig(with_dict):
    queue_url: str
    credentials: AWSCredentials


@dataclass
class ExecutionContext(with_dict):
    source_id: str
    source_config_id: str
    org_id: str
    plugin_id: str
    version_signature: str
    execution_id: str = field(default_factory=get_uuid)
    runner_id: Optional[str] = field(default=None)


@dataclass
class SchedulingWrapper(with_dict):
    execution_context: ExecutionContext
    delivery_delay: int = 0
