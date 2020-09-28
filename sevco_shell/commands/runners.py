import datetime
from pprint import pprint

from sevco_shell.builders.builder import Builder
from sevco_shell.clients.runner.client import RunnerServiceClient
from sevco_shell.clients.runner.models import Runner
from sevco_shell.commands.command import CommandBuilder, CommandWithList
from sevco_shell.config import Config


def RunnersCmd(config: Config):
    builder = CommandBuilder('runners', config.credentials)

    @builder.from_cls()
    class _RunnersCmd(CommandWithList):
        '''Runners - manage runners'''

        def __init__(self, config: Config):
            self.config = config
            super().__init__()

            self.client = RunnerServiceClient(
                api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)
            self.runners = None

        def get_things(self):
            epoch = datetime.datetime.utcfromtimestamp(
                0).replace(tzinfo=datetime.timezone.utc)
            return sorted(self.client.list(),
                          key=lambda x: x.last_checkin_time or epoch, reverse=True)

        def things_header(self):
            return [("Name", 20), ("Last Checkin", 40)]

        def format_thing(self, runner: Runner) -> str:
            return f"{runner.display_name.rjust(20)} {str(runner.last_checkin_time).rjust(40)}"

        @builder.empty_cmd()
        def _do_list(self):
            '''list available runners'''
            return self._list()

        @builder.cmd(permissions=['admin:runner:get', 'runner:get'])
        def do_info(self, idx: int):
            '''retrieve runner details'''
            selected = self.get_thing_by_index(self.arg_as_idx(idx))
            pprint(selected.as_dict())

        @builder.cmd(permissions=['admin:runner:delete', 'runner:delete'])
        def do_del(self, idx: int):
            '''unregister runner'''
            selected = self.get_thing_by_index(self.arg_as_idx(idx))
            if Builder.get_yes_no(f"Really delete runner {selected.display_name}?", default_yes=False):
                self.client.delete(selected.runner_id)

    return builder.build()(config)
