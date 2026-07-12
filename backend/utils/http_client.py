import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch_json(url: str, headers: dict[str, str] | None = None) -> Any:
    request = Request(url, headers=headers or {})
    with urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_json_safe(url: str, headers: dict[str, str] | None = None) -> tuple[Any, str | None]:
    try:
        return fetch_json(url, headers=headers), None
    except HTTPError as error:
        return None, f"HTTP {error.code}"
    except URLError as error:
        return None, str(error.reason)
    except Exception as error:
        return None, str(error)
