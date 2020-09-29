import cmd
from . import __version__ as version

import colorama
import requests

from sevco_shell.config import CredentialsProviderChain
from sevco_shell.config.credentials import ApiCredentials
from sevco_shell.scopes.scope import Scope
from sevco_shell.scopes.sv import SvScope


deep_v_banner = """
          ███████╗          ███████╗ 
 ██████╗███████╗██╗        ██╔═██████╗ ██████╗
██╔════╝██╔════╝ ██╗      ██╔╝██╔════╝██╔═══██╗
╚█████╗ █████╗    ██╗    ██╔╝ ██║     ██║   ██║
 ╚═══██╗██╔══╝     ██╗  ██╔╝  ██║     ██║   ██║
██████╔╝███████╗    ██ ██╔╝   ╚██████╗╚██████╔╝
╚═════╝ ╚══════╝     ███╔╝     ╚═════╝ ╚═════╝
                     ╚══╝ 
"""

welcome_text = f"""
Welcome to the Sevco Shell ({version}).

Type 'help' for available commands.
"""


class Shell(cmd.Cmd):
    banner = f"{colorama.Fore.RED}{deep_v_banner}{colorama.Style.RESET_ALL}"
    intro = f"{colorama.Fore.RED}{welcome_text}{colorama.Style.RESET_ALL}"

    def __init__(self, credentials: ApiCredentials):
        super().__init__()
        self.credentials = credentials
        colorama.init()

    def print_banner(self):
        try:
            # wrap this in case there is some issue with unicode to stdout
            print(self.banner)
        except:
            pass

        print(self.intro)

    def cmdloop(self, intro=None):
        self.print_banner()

        Scope.cmd_stack.append(SvScope(self.credentials))

        while Scope.cmd_stack:
            try:
                Scope.cmd_stack[-1].cmdloop(intro)
            except KeyboardInterrupt:
                print()
            except requests.exceptions.HTTPError as e:
                print(f"Error: {str(e)}")
                if e.response.status_code == 403:
                    print("Please verify API host and API key")
            except Exception as e:
                print(f"Error: {str(e)}")


def main():
    cred_provider = CredentialsProviderChain()
    credentials = ApiCredentials(cred_provider)

    shell = Shell(credentials)

    shell.cmdloop()


if __name__ == "__main__":
    main()
