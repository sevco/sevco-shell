import colorama
import cmd
import inspect
from typing import Any, List, Optional, Tuple, Type

from sevco_shell.config.credentials import ApiCredentials


class Command(cmd.Cmd):
    def __init__(self):
        super().__init__()


class CommandWithList(Command):
    def __init__(self):
        super().__init__()
        self._things = None

    @property
    def things(self) -> List[Any]:
        if self._things is None:
            self._things = self.get_things()

        return self._things

    def _clear_list(self):
        self._things = None

    def emptyline(self):
        self._do_list()

    def _list(self):
        self._clear_list()

        print()

        idx_width = len(f"[{len(self.things)}]")

        header = ''.rjust(idx_width)
        for label, width in self.things_header():
            header += f" {colorama.Fore.RED}{label.rjust(width)}{colorama.Style.RESET_ALL}"
            
        header += f"\n{''.rjust(idx_width)}"
        for _, width in self.things_header():
            header += f" {colorama.Style.DIM}{'='*width}{colorama.Style.RESET_ALL}"

        print(header)

        for x, thing in enumerate(self.things, start=1):
            idx = f"{colorama.Style.DIM}[{colorama.Style.NORMAL}{str(x).rjust(idx_width-2)}{colorama.Style.DIM}]{colorama.Style.NORMAL}"
            print(f"{idx} {self.format_thing(thing)}")

    def things_header(self) -> List[Tuple[str, int]]:
        raise NotImplementedError

    def _do_list(self):
        raise NotImplementedError

    def get_things(self) -> List[Any]:
        raise NotImplementedError

    def format_thing(self, thing) -> str:
        raise NotImplementedError

    def get_thing_by_index(self, idx: int):
        try:
            return self.things[idx-1]
        except IndexError:
            raise IndexError(f"Index must be between 1 and {len(self.things)}")

    def arg_as_idx(self, arg) -> int:
        try:
            return int(arg)
        except ValueError:
            raise Exception("Requires integer index")


class CommandBuilder:
    def __init__(self, basecmd: str, credentials: ApiCredentials = None):
        self.basecmd = basecmd
        self.credentials = credentials
        self.perms = {}
        self.cmd_class: Optional[Type[Command]] = None

    def from_cls(self):
        def decorator(cls):
            self.cmd_class = cls
            return cls
        return decorator

    def cmd(self, permissions: List[str]):
        def decorator(f):
            self.perms[f.__name__] = set(permissions)
            f.__doc__ = self.build_docstring(f)
            return f
        return decorator

    def empty_cmd(self):
        def decorator(f):
            arg = self.get_func_arg(f)
            if not arg or arg.startswith('_'):
                cmd = f"{self.basecmd}"
            else:
                cmd = f"{self.basecmd} [{arg}]"
            f.__doc__ = f"{cmd.ljust(30)}{inspect.getdoc(f)}"

            return f
        return decorator

    def build(self) -> Type:
        assert self.cmd_class

        jwt_permissions = set(self.credentials.permissions()
                              ) if self.credentials else set()

        for f in [f for f in dir(self.cmd_class) if f.startswith("do_")]:
            permissions = self.perms.get(f)
            if permissions and not permissions & jwt_permissions:
                delattr(self.cmd_class, f)

        help_text = f"{inspect.getdoc(self.cmd_class)}\n\n"
        for f in [f for f in dir(self.cmd_class) if (f.startswith("do_") or f.startswith('_do_')) and f != 'do_help']:
            func = getattr(self.cmd_class, f)
            help_text += f"{inspect.getdoc(func)}\n"

        def do_help(self, arg):
            if arg:
                return cmd.Cmd.do_help(self, arg)

            print(help_text)
            return False

        setattr(self.cmd_class, 'do_help', do_help)

        return self.cmd_class

    def build_docstring(self, func) -> str:
        arg = self.get_func_arg(func)
        if arg.startswith('_'):
            cmd = f"{self.basecmd} {func.__name__[3:]}"
        else:
            cmd = f"{self.basecmd} {func.__name__[3:]} [{arg}]"

        return f"{cmd.ljust(30)}{inspect.getdoc(func)}"

    def get_func_arg(self, func) -> Optional[str]:
        args = inspect.getfullargspec(func).args
        args.remove('self')
        if args:
            return args[0]
        return None
