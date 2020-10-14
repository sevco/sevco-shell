from getpass import getpass
from typing import List


class Builder:
    @staticmethod
    def get_input(prompt: str, required: bool = True) -> str:
        if required:
            prompt = f"{prompt} (required)"

        val = input(f"{prompt}: ")
        while val == "" and required:
            val = input(f"{prompt}: ")

        return val

    @staticmethod
    def get_yes_no(prompt: str, default_yes: bool = True) -> bool:
        p = f"{prompt} (Yes/[N]o): "
        if default_yes:
            p = f"{prompt} ([Y]es/No): "
        val = input(p)
        while val.lower() not in ['y', 'yes', 'n', 'no', '']:
            val = input(p)

        if val == '':
            return default_yes

        return val.lower()[0] == 'y'

    @staticmethod
    def get_one_of(prompt: str, values=List[str], default=None) -> str:
        choices = ', '.join([v if v != default else f"[{v}]" for v in values])
        val = input(f"{prompt} ({choices}): ") or default
        while val not in values:
            val = input(f"{prompt} ({choices}): ") or default

        return val

    @staticmethod
    def get_password(prompt: str) -> str:
        while True:
            v = getpass(f"{prompt} (required): ")
            p = getpass(f"{prompt} (re-enter): ")
            if v == p:
                break
            print("Mismatch")

        return v
