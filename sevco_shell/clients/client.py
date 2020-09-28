from typing import Callable, Dict, Optional

import requests


class SevcoClient:
    def __init__(self, api_host: str, auth_token: Optional[str] = None, target_org: Optional[str] = None):
        self.auth_token = auth_token
        self.api_host = api_host
        self.target_org = target_org

    @property
    def static_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": self.auth_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if self.target_org:
            headers['X-Sevco-Target-Org'] = self.target_org

        return headers

    def api_get(self, path: str, **kwargs) -> requests.Response:
        return self._make_request(requests.get, url=f"{self.api_host}{path}", **kwargs)

    def api_put(self, path: str, **kwargs) -> requests.Response:
        return self._make_request(requests.put, url=f"{self.api_host}{path}", **kwargs)

    def api_post(self, path: str, **kwargs) -> requests.Response:
        return self._make_request(requests.post, url=f"{self.api_host}{path}", **kwargs)

    def api_delete(self, path: str, **kwargs) -> requests.Response:
        return self._make_request(requests.delete, url=f"{self.api_host}{path}", **kwargs)

    def _make_request(self,
                      method: Callable,
                      url: str,
                      headers: Dict = None,
                      data: Dict = None,
                      json_data: Dict = None,
                      params: Dict = None,
                      files: Dict = None) -> requests.Response:
        request_headers = {**self.static_headers}

        if headers:
            request_headers.update(headers)

        resp = method(url, headers=request_headers, params=params,
                      data=data, json=json_data, files=files)

        resp.raise_for_status()

        return resp
