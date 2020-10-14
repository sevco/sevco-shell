import json
from typing import List

from sevco_shell.clients.client import SevcoClient
from sevco_shell.clients.runner.models import (Runner, RunnerConfig,
                                               SchedulingWrapper)


class RunnerServiceClient(SevcoClient):
    def get(self, runner_id: str) -> Runner:
        resp = self.api_get(f"/v1/runner/{runner_id}")
        return Runner.from_dict(json.loads(resp.text))

    def list(self) -> List[Runner]:
        resp = self.api_get("/v1/runner")

        return [Runner.from_dict(d) for d in json.loads(resp.text)]

    def add(self, runner: Runner) -> Runner:
        resp = self.api_post("/v1/runner", data=json.dumps(runner.as_dict()))

        return Runner.from_dict(json.loads(resp.text))

    def delete(self, runner_id: str) -> None:
        self.api_delete(f"/v1/runner/{runner_id}")

    def update(self, runner: Runner) -> Runner:
        resp = self.api_put(
            f"/v1/runner/{runner.runner_id}", data=json.dumps(runner.as_dict()))

        return Runner.from_dict(json.loads(resp.text))

    def execute(self, wrapper: SchedulingWrapper) -> SchedulingWrapper:
        resp = self.api_post(f"/v1/runner/execute",
                             data=json.dumps(wrapper.as_dict()))

        return SchedulingWrapper.from_dict(json.loads(resp.text))

    def ping(self, runner_id: str) -> Runner:
        resp = self.api_post(f"/v1/runner/{runner_id}/ping")

        return Runner.from_dict(json.loads(resp.text))

    def get_config(self, runner_id: str) -> RunnerConfig:
        resp = self.api_get(f"/v1/runner/{runner_id}/config")

        return RunnerConfig.from_dict(json.loads(resp.text))

    def download(self, runner_os: str) -> bytes:
        resp = self.api_get(f"/v1/runner/download?os={runner_os}")

        return resp.content
