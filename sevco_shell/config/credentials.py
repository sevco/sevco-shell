import argparse
import os
import time
from pathlib import Path
from typing import List, Optional

import jwt
import toml

from sevco_shell.builders.builder import Builder


class CredentialsProvider:
    def api_host(self) -> Optional[str]:
        raise NotImplementedError

    def auth_token(self) -> Optional[str]:
        raise NotImplementedError


class EnvironmentCredentialsProvider(CredentialsProvider):
    def api_host(self) -> Optional[str]:
        return os.environ.get("SVSH_API_HOST", None)

    def auth_token(self) -> Optional[str]:
        return os.environ.get("SVSH_AUTH_TOKEN", None)


class ArgumentCredentialsProvider(CredentialsProvider):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--api-host', help='API Host',
                            default=None, required=False)
        parser.add_argument('--auth-token', help='Bearer Token: Bearer JWT',
                            default=None, required=False)
        self.args, _ = parser.parse_known_args()

    def api_host(self) -> Optional[str]:
        return self.args.api_host

    def auth_token(self) -> Optional[str]:
        return self.args.auth_token


class FileCredentialsProvider(CredentialsProvider):
    def __init__(self):
        cred_path = f"{Path.home()}/.sevco/credentials"
        self.profile = os.environ.get("SEVCO_PROFILE", "default")

        self.profiles = {}
        try:
            if os.path.exists(cred_path):
                with open(cred_path) as f:
                    self.profiles = toml.loads(f.read())
        except:
            pass

    def api_host(self) -> Optional[str]:
        return self.profiles.get(self.profile, {}).get("api_host")

    def auth_token(self) -> Optional[str]:
        return self.profiles.get(self.profile, {}).get("auth_token")

    @staticmethod
    def persist(api_host: Optional[str] = None, auth_token: Optional[str] = None):
        cred_dir = f"{Path.home()}/.sevco"
        try:
            os.makedirs(cred_dir)
        except FileExistsError:
            pass

        cred_path = f"{cred_dir}/credentials"
        profile = os.environ.get("SEVCO_PROFILE", "default")

        profiles = {profile: {}}
        try:
            if os.path.exists(cred_path):
                with open(cred_path) as f:
                    profiles = toml.loads(f.read())
        except:
            pass

        if api_host:
            profiles[profile]['api_host'] = api_host
        if auth_token:
            profiles[profile]['auth_token'] = auth_token

        with open(cred_path, 'w') as f:
            f.write(toml.dumps(profiles))


class CredentialsProviderChain(CredentialsProvider):
    def __init__(self, chain: List[CredentialsProvider] = None):
        self.chain = chain or [
            ArgumentCredentialsProvider(), EnvironmentCredentialsProvider(), FileCredentialsProvider()]

    def api_host(self) -> Optional[str]:
        for provider in self.chain:
            api_host = provider.api_host()
            if api_host:
                return api_host
        return None

    def auth_token(self) -> Optional[str]:
        for provider in self.chain:
            auth_token = provider.auth_token()
            if auth_token:
                return auth_token
        return None


class BearerToken:
    def __init__(self, token: str):
        self.token = token

    def jwt(self):
        # Slice out the 'Bearer ' prefix
        return jwt.decode(self.token[7:], verify=False)

    def permissions(self) -> List[str]:
        return self.jwt()['permissions']

    def expired(self) -> bool:
        return time.time() > self.jwt()['exp'] + (5 * 60)

    def validate(self) -> bool:
        return self.validate_token(self.token)

    @staticmethod
    def validate_token(token: str) -> bool:
        if not token.startswith('Bearer '):
            print("Invalid format.  Expected 'Bearer abcd1234'")
            return False

        try:
            decoded = jwt.decode(token[7:], verify=False)
            if time.time() > decoded['exp']:
                print("Token is expired")
                return False
        except:
            print("Unable to decode API Token")
            return False

        return True


class ApiCredentials:
    def __init__(self, provider: CredentialsProvider):
        self.provider = provider
        self._api_host: Optional[str] = None
        self._bearer_token: Optional[BearerToken] = None

    @property
    def api_host(self) -> str:
        if not self._api_host:
            self._api_host = self.provider.api_host()
            if not self._api_host:
                self._api_host = Builder.get_input(
                    "Please provide the Sevco API host")
                while not self._api_host:
                    self._api_host = Builder.get_input(
                        "Please provide the Sevco API host")

                if Builder.get_yes_no("Save API host to ~/.sevco/credentials?", default_yes=True):
                    self.persist(api_host=self._api_host)

        return self._api_host

    @property
    def auth_token(self) -> str:
        return self.bearer_token.token

    @property
    def bearer_token(self) -> BearerToken:
        # If we don't have a token yet try to get one from the credentials provider
        if not self._bearer_token:
            auth_token = self.provider.auth_token()
            if auth_token:
                self._bearer_token = BearerToken(auth_token)

        # If we still don't have a token yet ask the user to provide one
        if not self._bearer_token or not BearerToken.validate_token(self._bearer_token.token):
            self._bearer_token = self.auth_token_from_user()

            if Builder.get_yes_no("Save API Token to ~/.sevco/credentials?", default_yes=True):
                self.persist(auth_token=self._bearer_token.token)

        # Make sure any existing tokens are still valid
        if not self._bearer_token.validate():
            self._bearer_token = self.auth_token_from_user()

            if Builder.get_yes_no("Save API Token to ~/.sevco/credentials?", default_yes=True):
                self.persist(auth_token=self._bearer_token.token)

        # Make sure the token we are using has not expired
        if self._bearer_token.expired():
            print("API Token has expired")
            self._bearer_token = self.auth_token_from_user()

            if Builder.get_yes_no("Save API Token to ~/.sevco/credentials?", default_yes=True):
                self.persist(auth_token=self._bearer_token.token)

        return self._bearer_token

    def permissions(self) -> List[str]:
        return self.bearer_token.permissions()

    def auth_token_from_user(self) -> BearerToken:
        prompt = "Please provide the Sevco API Bearer Token (format: Bearer abcd1234)"
        auth_token = Builder.get_input(prompt, required=False)

        while not auth_token or not BearerToken.validate_token(auth_token):
            auth_token = Builder.get_input(prompt, required=False)

        return BearerToken(auth_token)

    def persist(self, api_host: Optional[str] = None, auth_token: Optional[str] = None):
        FileCredentialsProvider.persist(api_host, auth_token)
