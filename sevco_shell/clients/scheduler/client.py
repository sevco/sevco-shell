import json

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.runner.models import SchedulingWrapper
from sevco_shell.clients.scheduler.models import DataSourceSchedule


class SchedulerServiceClient(SevcoClient):
    def get(self, source_id: str) -> DataSourceSchedule:
        resp = self.api_get(self._get_path(source_id))
        return DataSourceSchedule.from_dict(json.loads(resp.text))

    def add(self, schedule: DataSourceSchedule) -> DataSourceSchedule:
        resp = self.api_post(self._get_path(schedule.source_id),
                             data=json.dumps(schedule.as_dict()))

        return DataSourceSchedule.from_dict(json.loads(resp.text))

    def delete(self, source_id: str) -> None:
        self.api_delete(self._get_path(source_id))

    def update(self, schedule: DataSourceSchedule) -> DataSourceSchedule:
        resp = self.api_put(self._get_path(schedule.source_id),
                            data=json.dumps(schedule.as_dict()))

        return DataSourceSchedule.from_dict(json.loads(resp.text))

    def execute(self, source_config_id: str) -> SchedulingWrapper:
        resp = self.api_post(
            f"/v1/integration/source/config/{source_config_id}/execution")

        return SchedulingWrapper.from_dict(json.loads(resp.text))

    @staticmethod
    def _get_path(source_id):
        return f"/v1/integration/source/{source_id}/schedule"
