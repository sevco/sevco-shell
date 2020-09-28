from sevco_shell.builders.builder import Builder
from sevco_shell.builders.source import SourceScheduleBuilder
from sevco_shell.clients.scheduler.client import SchedulerServiceClient
from sevco_shell.clients.source_catalog.models import Source
from sevco_shell.commands.command import Command, CommandBuilder
from sevco_shell.config import Config


def ScheduleCmd(config: Config, source: Source):
    builder = CommandBuilder('schedule', config.credentials)

    @builder.from_cls()
    class _SchedulesCmd(Command):
        '''Schedules - view and manage source execution schedules'''

        def __init__(self, config: Config, source: Source):
            self.config = config
            super().__init__()

            self.source = source
            self.client = SchedulerServiceClient(
                api_host=config.credentials.api_host, auth_token=config.credentials.auth_token, target_org=config.org.id)

        def emptyline(self):
            return self.do_help('')

        @builder.cmd(permissions=['admin:source:schedule:get', 'source:schedule:get'])
        def do_info(self, _arg):
            '''retrieve schedule details'''
            try:
                sched = self.client.get(self.source.id)
                print(sched.schedule_config)
            except:
                print("No schedule set")

        @builder.cmd(permissions=['admin:source:schedule:delete', 'source:schedule:delete'])
        def do_del(self, _arg):
            '''delete source schedule - disables automatic data collection'''
            if Builder.get_yes_no("Really delete schedule?"):
                self.client.delete(self.source.id)
                print(f"{source.display_name} schedule removed")

        @builder.cmd(permissions=['admin:source:schedule:create', 'source:schedule:create', 'admin:source:schedule:update', 'source:schedule:update'])
        def do_set(self, _arg):
            '''Set source schedule'''
            update = False
            try:
                self.client.get(self.source.id)
                update = True
            except:
                pass

            SourceScheduleBuilder(
                self.config, self.source.id).from_user().build(update=update)

    return builder.build()(config, source)
