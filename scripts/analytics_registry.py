#!/usr/bin/env python3
"""Load and validate data/analytics.json (fleet-shared shape)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANALYTICS_PATH = ROOT / "data" / "analytics.json"

GA4_ID_RE = re.compile(r"^G-[A-Z0-9]+$")
CF_TOKEN_RE = re.compile(r"^[a-f0-9]{32}$")
HOST_RE = re.compile(r"^[a-z0-9.-]+$")
COOKIE_RE = re.compile(r"^[A-Za-z0-9_-]+$")


class AnalyticsRegistry:
    """Typed view of the analytics registry."""

    def __init__(
        self,
        *,
        internal_cookie: str,
        legacy_cookies: list[str],
        spa: bool,
        hosts: dict[str, dict[str, str]],
    ) -> None:
        self.internal_cookie = internal_cookie
        self.legacy_cookies = legacy_cookies
        self.spa = spa
        self.hosts = hosts

    @property
    def hostnames(self) -> tuple[str, ...]:
        return tuple(self.hosts.keys())

    @property
    def honour_cookies(self) -> tuple[str, ...]:
        """Primary plus unique legacy names (hub primary may equal legacy)."""
        seen: list[str] = []
        for name in (self.internal_cookie, *self.legacy_cookies):
            if name not in seen:
                seen.append(name)
        return tuple(seen)

    def ga4_ids(self) -> set[str]:
        return {entry["ga4_id"] for entry in self.hosts.values()}

    def cf_tokens(self) -> set[str]:
        return {entry["cf_beacon_token"] for entry in self.hosts.values()}

    def primary_ga4_id(self) -> str:
        ids = sorted(self.ga4_ids())
        if len(ids) != 1:
            raise SystemExit(
                "analytics registry expects one GA4 id across hosts for this site build, "
                f"got {ids!r}"
            )
        return ids[0]

    def primary_cf_token(self) -> str:
        tokens = sorted(self.cf_tokens())
        if len(tokens) != 1:
            raise SystemExit(
                "analytics registry expects one CF beacon token across hosts for this site "
                f"build, got {tokens!r}"
            )
        return tokens[0]


def _require_str(obj: dict[str, Any], key: str, *, path: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"{path}: {key} must be a non-empty string")
    return value.strip()


def validate_analytics_payload(payload: Any, *, path: str = "data/analytics.json") -> AnalyticsRegistry:
    """Validate registry shape used by hub and (later) sister sites."""
    if not isinstance(payload, dict):
        raise SystemExit(f"{path} must be a JSON object")

    internal_cookie = _require_str(payload, "internal_cookie", path=path)
    if not COOKIE_RE.fullmatch(internal_cookie):
        raise SystemExit(f"{path}: internal_cookie has invalid characters: {internal_cookie!r}")

    legacy_raw = payload.get("legacy_cookies")
    if not isinstance(legacy_raw, list):
        raise SystemExit(f"{path}: legacy_cookies must be an array of strings")
    legacy_cookies: list[str] = []
    for i, name in enumerate(legacy_raw):
        if not isinstance(name, str) or not name.strip():
            raise SystemExit(f"{path}: legacy_cookies[{i}] must be a non-empty string")
        name = name.strip()
        if not COOKIE_RE.fullmatch(name):
            raise SystemExit(f"{path}: legacy_cookies[{i}] has invalid characters: {name!r}")
        legacy_cookies.append(name)

    spa = payload.get("spa")
    if not isinstance(spa, bool):
        raise SystemExit(f"{path}: spa must be a boolean")

    hosts_raw = payload.get("hosts")
    if not isinstance(hosts_raw, dict) or not hosts_raw:
        raise SystemExit(f"{path}: hosts must be a non-empty object keyed by hostname")

    hosts: dict[str, dict[str, str]] = {}
    for host, entry in hosts_raw.items():
        if not isinstance(host, str) or not HOST_RE.fullmatch(host):
            raise SystemExit(f"{path}: invalid host key {host!r}")
        if not isinstance(entry, dict):
            raise SystemExit(f"{path}: hosts[{host!r}] must be an object")
        ga4_id = _require_str(entry, "ga4_id", path=f"{path}.hosts[{host!r}]")
        if not GA4_ID_RE.fullmatch(ga4_id):
            raise SystemExit(f"{path}: hosts[{host!r}].ga4_id invalid: {ga4_id!r}")
        token = _require_str(entry, "cf_beacon_token", path=f"{path}.hosts[{host!r}]")
        if not CF_TOKEN_RE.fullmatch(token):
            raise SystemExit(f"{path}: hosts[{host!r}].cf_beacon_token invalid: {token!r}")
        hosts[host] = {"ga4_id": ga4_id, "cf_beacon_token": token}

    unknown = set(payload) - {"internal_cookie", "legacy_cookies", "spa", "hosts"}
    if unknown:
        raise SystemExit(f"{path}: unknown keys: {sorted(unknown)}")

    return AnalyticsRegistry(
        internal_cookie=internal_cookie,
        legacy_cookies=legacy_cookies,
        spa=spa,
        hosts=hosts,
    )


def load_analytics(path: Path = ANALYTICS_PATH) -> AnalyticsRegistry:
    if not path.is_file():
        raise SystemExit(f"missing analytics registry: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON: {exc}") from exc
    return validate_analytics_payload(payload, path=str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path))
