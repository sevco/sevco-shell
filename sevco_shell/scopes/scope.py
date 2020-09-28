import cmd
from types import BuiltinMethodType
from typing import Dict, List, Union

import colorama

from sevco_shell.commands.command import Command
from sevco_shell.builders.builder import Builder


class PromptBuilder:
    def __init__(self, tokens: List[str], sep: str):
        self.sep = sep
        self.tokens = tokens

    @classmethod
    def from_cmd_stack(cls, cmds: List['Scope'], sep: str = ' > ') -> 'PromptBuilder':
        return cls([cmd.prompt_token for cmd in cmds], sep)

    def append(self, token) -> 'PromptBuilder':
        self.tokens.append(token)
        return self

    def build(self) -> str:
        tokens_sep = f"{colorama.Style.DIM}{self.sep}{colorama.Style.RESET_ALL}".join(
            [f"{colorama.Fore.RED}{token}{colorama.Style.RESET_ALL}" for token in self.tokens])
        return f"[{tokens_sep}]\n> "


class CmdResponse:
    def process(self):
        raise NotImplementedError


class ExitResponse(CmdResponse):
    def process(self) -> bool:
        Scope.cmd_stack.clear()
        return True


class NewScopeResponse(CmdResponse):
    def __init__(self, scope):
        self.scope = scope

    def process(self) -> bool:
        Scope.cmd_stack.append(self.scope)
        return True


class PopScopeResponse(CmdResponse):
    def process(self) -> bool:
        Scope.cmd_stack.pop()
        return True


class Scope(cmd.Cmd):
    cmd_stack: List['Scope'] = []
    doc_header = "Available commands (type help <topic>):"

    def __init__(self, prompt_token: str):
        super().__init__()

        self.prompt_token = prompt_token
        self.commands: Dict[str, Command] = {}

    def register_cmd(self, cmd_name: str, command: Command):
        def _do_cmd(arg):
            return command.onecmd(arg)

        def _help_cmd():
            return command.onecmd('help')

        def _complete_cmd(text, *ignored):
            return command.completenames(text)

        setattr(self, f'do_{cmd_name}', _do_cmd)
        setattr(self, f'help_{cmd_name}', _help_cmd)
        setattr(self, f'complete_{cmd_name}', _complete_cmd)

        self.commands[cmd_name] = command

    @property
    def prompt(self):
        return PromptBuilder.from_cmd_stack(self.cmd_stack).build()

    def do_back(self, arg):
        '''Return to previous scope'''
        return PopScopeResponse()

    def do_quit(self, arg):
        '''Exit the shell'''
        if Builder.get_yes_no("Are you sure you want to exit?", default_yes=True):
            print("Goodbye")
            return ExitResponse()

    def do_exit(self, arg):
        '''Exit the shell'''
        if Builder.get_yes_no("Are you sure you want to exit?", default_yes=True):
            print("Goodbye")
            return ExitResponse()

    def default(self, line):
        if line == 'EOF':
            if len(self.cmd_stack) == 1:
                if Builder.get_yes_no("Are you sure you want to exit?", default_yes=True):
                    print("Goodbye")
                    return ExitResponse()
            print()
            return PopScopeResponse()
        super().default(line)

    def emptyline(self):
        return False

    def postcmd(self, resp: Union[bool, CmdResponse], line):
        # If a do_* call returns a Cmd... push it onto the stack.
        #  If it returned False then pop the current Cmd from the stack
        if resp is not None and isinstance(resp, CmdResponse):
            return resp.process()

        return resp

    def get_names(self):
        return [f'do_{c}' for c in self.commands] + [f'help_{c}' for c in self.commands] + ['do_help', 'do_back', 'do_quit', 'do_exit']
