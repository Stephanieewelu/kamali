from dataclasses import dataclass
from typing import Any, Optional

import httpx


@dataclass
class HttpResponse:
    status_code: int
    data: Any
    error: Optional[str] = None


class HttpClient:
    def __init__(self, timeout: float = 10.0) -> None:
        self.timeout = timeout

    def get(self, url: str, headers: Optional[dict] = None) -> HttpResponse:
        try:
            response = httpx.get(url, headers=headers, timeout=self.timeout)
            return HttpResponse(status_code=response.status_code, data=response.text)
        except httpx.HTTPError as exc:
            return HttpResponse(status_code=0, data=None, error=str(exc))
