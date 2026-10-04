"""Cached API client, retry policy and host-specific authentication helpers."""
from http.client import IncompleteRead
import json
import logging
import os
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from storage import cache_path, read_json, write_json

LOG = logging.getLogger("softcatala-reuse")


class APIError(Exception):
    def __init__(self, status: int, url: str):
        self.status = status
        super().__init__(f"HTTP {status}: {url}")


class Client:
    def __init__(self, base: str, token: str, cache: Path, *, gitlab=False,
                 offline=False, refresh=False, max_wait=60, search_delay=6.2, generic=False, refresh_search=False):
        self.base = base.rstrip("/")
        self.token = token
        self.cache = cache
        self.gitlab = gitlab
        self.generic = generic
        self.offline = offline
        self.refresh = refresh
        self.refresh_search = refresh_search
        self.max_wait = max_wait
        self.search_delay = search_delay
        self.last_search = 0.0
        cache.mkdir(parents=True, exist_ok=True)

    def get(self, endpoint: str, params=None, *, text_response=False):
        url = self.base + endpoint
        if params:
            url += "?" + urlencode(params)
        dest = cache_path(self.cache, url)
        is_search = "/search" in endpoint
        force_refresh = self.refresh or (is_search and self.refresh_search)
        if dest.exists() and (not force_refresh or self.offline):
            return read_json(dest)
        if self.offline:
            raise APIError(0, url)
        if is_search and not self.gitlab and not self.generic:
            delay = self.search_delay - (time.monotonic() - self.last_search)
            if delay > 0:
                time.sleep(delay)
            self.last_search = time.monotonic()
        headers = {"User-Agent": "softcatala-reuse-audit/1.0", "Accept": "text/plain" if text_response else "application/json"}
        if self.token:
            headers["PRIVATE-TOKEN" if self.gitlab else "Authorization"] = (
                self.token if self.gitlab else "Bearer " + self.token)
        if not self.gitlab and not self.generic:
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        for attempt in range(3):
            try:
                with urlopen(Request(url, headers=headers), timeout=30) as response:
                    data = response.read().decode("utf-8") if text_response else json.load(response)
                write_json(dest, data, indent=None)
                return data
            except HTTPError as exc:
                retry_after = exc.headers.get("Retry-After")
                reset = exc.headers.get("X-RateLimit-Reset")
                remaining = exc.headers.get("X-RateLimit-Remaining")
                wait = None
                if retry_after and retry_after.isdigit():
                    wait = int(retry_after)
                elif reset and remaining == "0":
                    wait = max(1, int(reset) - int(time.time()) + 1)
                elif exc.code in (429, 500, 502, 503, 504):
                    wait = 2 ** (attempt + 1)
                if wait is not None and wait <= self.max_wait and attempt < 2:
                    LOG.warning("HTTP %s; retrying in %ss", exc.code, wait)
                    time.sleep(wait)
                    continue
                raise APIError(exc.code, url) from None
            except (URLError, TimeoutError, json.JSONDecodeError, IncompleteRead, ConnectionError) as exc:
                if attempt == 2:
                    raise APIError(0, url) from exc
                time.sleep(2 ** attempt)
        raise APIError(0, url)

    def pages(self, endpoint, params, warnings, *, max_pages=0, label=""):
        page = 1
        while True:
            batch = self.get(endpoint, {**params, "per_page": 100, "page": page})
            if not isinstance(batch, list):
                raise APIError(0, self.base + endpoint)
            yield from batch
            if len(batch) < 100:
                break
            if max_pages and page >= max_pages:
                warnings.append(f"Pagination limited: {label or endpoint}, {page} pages")
                break
            page += 1


def github_token():
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if token:
        return token
    try:
        result = subprocess.run(["gh", "auth", "token"], capture_output=True,
                                text=True, timeout=10, check=False)
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


