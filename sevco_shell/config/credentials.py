import argparse
import os
import time
from pathlib import Path
from typing import List, Optional

import jwt
import requests
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


class AuthToken:
    def __init__(self, token: str):
        self.token = token

    def permissions(self, api_host: str) -> List[str]:
        raise NotImplementedError

    def expired(self) -> bool:
        raise NotImplementedError

    def validate(self) -> bool:
        raise NotImplementedError


class BearerToken(AuthToken):
    def __init__(self, token: str):
        self.token = token

    def _jwt(self):
        # Slice out the 'Bearer ' prefix
        return jwt.decode(self.token[7:], verify=False)

    def permissions(self, api_host: str) -> List[str]:
        permissions = self._jwt().get('permissions', [])

        for r in self._jwt().get('https://sevco/props/permsByRole', []):
            permissions.extend(r['permissions'])

        return permissions

    def expired(self) -> bool:
        return time.time() > self._jwt()['exp'] + (5 * 60)

    def validate(self) -> bool:
        if not self.token.startswith('Bearer '):
            print("Invalid format.  Expected 'Bearer abcd1234'")
            return False

        try:
            decoded = jwt.decode(self.token[7:], verify=False)
            if time.time() > decoded['exp']:
                print("Token is expired")
                return False
        except Exception as e:
            print(f"Unable to decode API Token: {e}")
            return False

        return True


class ApiToken(AuthToken):
    def __init__(self, token: str):
        self.token = token
        self._permissions: List[str] = []

    def permissions(self, api_host: str) -> List[str]:
        if not self._permissions:
            resp = requests.get(
                f"{api_host}/v1/admin/user/me/apikey/{self.token[6:]}/claims", headers={"Authorization": self.token})
            resp.raise_for_status()

            self._permissions = []

            for r in resp.json().get('claims', {}).get('https://sevco/props/permsByRole', []):
                self._permissions.extend(r['permissions'])

        return self._permissions

    def expired(self) -> bool:
        return False

    def validate(self) -> bool:
        return True


def auth_token(token: str) -> AuthToken:
    if token.startswith("Bearer "):
        return BearerToken(token)
    elif token.startswith("Token "):
        return ApiToken(token)
    else:
        raise Exception("Token must start with Bearer or Token")


class ApiCredentials:
    def __init__(self, provider: CredentialsProvider):
        self.provider = provider
        self._api_host: Optional[str] = None
        self._auth_token: Optional[AuthToken] = None

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
        return self._get_auth_token().token

    def _get_auth_token(self) -> AuthToken:
        # If we don't have a token yet try to get one from the credentials provider
        if not self._auth_token:
            token = self.provider.auth_token()
            if token:
                self._auth_token = auth_token(token)

        # If we still don't have a token yet ask the user to provide one
        if not self._auth_token:
            self._auth_token = self.auth_token_from_user()

            if Builder.get_yes_no("Save API Token to ~/.sevco/credentials?", default_yes=True):
                self.persist(auth_token=self._auth_token.token)

        # Make sure any existing tokens are still valid
        if not self._auth_token.validate():
            self._auth_token = self.auth_token_from_user()

            if Builder.get_yes_no("Save API Token to ~/.sevco/credentials?", default_yes=True):
                self.persist(auth_token=self._auth_token.token)

        # Make sure the token we are using has not expired
        if self._auth_token.expired():
            print("API Token has expired")
            self._auth_token = self.auth_token_from_user()

            if Builder.get_yes_no("Save API Token to ~/.sevco/credentials?", default_yes=True):
                self.persist(auth_token=self._auth_token.token)

        return self._auth_token

    def permissions(self) -> List[str]:
        return self._get_auth_token().permissions(self.api_host)

    def auth_token_from_user(self) -> AuthToken:
        import readline  # fix for truncated input on osx

        prompt = "Please provide the Sevco API Bearer Token (format: Bearer or Token)"
        token = Builder.get_input(prompt, required=False)

        while not token or not auth_token(token).validate():
            token = Builder.get_input(prompt, required=False)

        return auth_token(token)

    def persist(self, api_host: Optional[str] = None, auth_token: Optional[str] = None):
        FileCredentialsProvider.persist(api_host, auth_token)
