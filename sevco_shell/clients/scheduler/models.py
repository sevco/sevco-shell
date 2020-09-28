from dataclasses import dataclass

from sevco_shell.clients.models import with_dict


@dataclass
class DataSourceSchedule(with_dict):
    source_id: str
#    source_type: str
    schedule_config: str
