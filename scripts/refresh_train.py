#!/usr/bin/env python3
"""Rewrite stack-releases.json from each component's default branch.

The train is the one version record for the stack. It used to freeze a
reviewed snapshot, and that snapshot stayed on project-continuity-modules
0.6.0 after 0.7.0 had shipped. This script reads components.json, asks GitHub
for the default-branch head of each component, and records the version that
head declares. A scheduled workflow runs it so the record cannot lag behind
the branches adopters are actually on.

Usage:
    python scripts/refresh_train.py           # write stack-releases.json when a head moved
    python scripts/refresh_train.py --check   # exit 1 when the file is stale; do not write

Exit codes: 0 the file matches the heads, 1 a component could not be read or
--check found drift.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_PATH = ROOT / "components.json"
RELEASES_PATH = ROOT / "stack-releases.json"
TRAIN_SCHEMA = "agent-stack-train.stack-releases.v1"
PUBLISHED_BY = "https://github.com/Pukujan/agent-stack-train"
RELEASE_TRAIN = "current"
ADOPTION_RULE = (
    "This file is the mesh for project-continuity-modules, "
    "content-generation-modules, agent-custom-setup, and observational-issue-ops. "
    "Each of those repositories must require every component here, including "
    "itself. An older version or commit fails scripts/mesh.py. The hotloader "
    "installs these versions and refuses an older checkout."
)
NOTE = (
    "When one component moves, the other three must move to it. "
    "scripts/refresh_train.py records the current head of each component. "
    "scripts/mesh.py fails a repository that still requires an older one. "
    "recorded_at changes only when a certified entry or this rule changes."
)


class RefreshError(Exception):
    """One component could not be read. The train file is left untouched."""


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RefreshError(f"{path} is missing") from None
    except json.JSONDecodeError as exc:
        raise RefreshError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RefreshError(f"{path} must contain a JSON object")
    return data


def token_from_env() -> str | None:
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or None


def http_get(url: str, token: str | None = None, accept: str = "application/vnd.github+json") -> str:
    headers = {
        "User-Agent": "agent-stack-train-refresh",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RefreshError(f"GET {url} failed: HTTP {exc.code} {detail}") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise RefreshError(f"GET {url} failed: {exc}") from exc


def api_json(url: str, fetch) -> dict:
    try:
        data = json.loads(fetch(url))
    except json.JSONDecodeError as exc:
        raise RefreshError(f"{url} did not return JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RefreshError(f"{url} must return a JSON object")
    return data


def one_match(text: str, pattern: str, label: str) -> str:
    found = list(dict.fromkeys(re.findall(pattern, text)))
    if len(found) != 1:
        raise RefreshError(f"{label} matched {found or 'nothing'}; expected one value")
    value = found[0].strip()
    if not value:
        raise RefreshError(f"{label} matched an empty value")
    return value


def json_key(document: dict, key: str, label: str):
    if key not in document:
        raise RefreshError(f"{label} has no {key!r}")
    return document[key]


def release_version(tag: str) -> str:
    version = tag[1:] if tag.startswith("v") else tag
    if not version:
        raise RefreshError(f"release tag {tag!r} has no version")
    return version


def head_sha(owner: str, repo: str, ref: str, fetch) -> str:
    payload = api_json(f"https://api.github.com/repos/{owner}/{repo}/commits/{ref}", fetch)
    sha = payload.get("sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", sha):
        raise RefreshError(f"{owner}/{repo}@{ref} did not return a commit sha")
    return sha.lower()


def file_text(owner: str, repo: str, sha: str, path: str, fetch) -> str:
    # The contents API, not raw.githubusercontent.com. The raw host failed TLS
    # from the network this script runs on; api.github.com did not.
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={sha}"
    body = fetch(url)
    stripped = body.lstrip()
    if not stripped.startswith("{"):
        return body
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body
    if isinstance(payload, dict) and payload.get("encoding") == "base64" and isinstance(payload.get("content"), str):
        return base64.b64decode(payload["content"]).decode("utf-8")
    return body


def component_entry(spec: dict, owner: str, ref: str, fetch) -> dict:
    name = spec["name"]
    repo = spec["repo"]
    sha = head_sha(owner, repo, ref, fetch)
    entry: dict = {"version": "", "commit": sha}

    if spec.get("version_file"):
        text = file_text(owner, repo, sha, spec["version_file"], fetch)
        entry["version"] = one_match(
            text, spec["version_pattern"], f"{name} {spec['version_file']}"
        )
    elif spec.get("version_json"):
        text = file_text(owner, repo, sha, spec["version_json"], fetch)
        try:
            document = json.loads(text)
        except json.JSONDecodeError as exc:
            raise RefreshError(f"{name} {spec['version_json']} is not valid JSON: {exc}") from exc
        if not isinstance(document, dict):
            raise RefreshError(f"{name} {spec['version_json']} must be a JSON object")
        version = json_key(document, spec["version_key"], f"{name} {spec['version_json']}")
        if not isinstance(version, str) or not version.strip():
            raise RefreshError(f"{name} version must be a non-empty string")
        entry["version"] = version
        if spec.get("modules_key"):
            modules = json_key(document, spec["modules_key"], f"{name} {spec['version_json']}")
            if not isinstance(modules, list) or not modules:
                raise RefreshError(f"{name} {spec['modules_key']} must be a non-empty list")
            entry["modules"] = len(modules)
    elif spec.get("version_from_release"):
        payload = api_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", fetch)
        tag = payload.get("tag_name")
        if not isinstance(tag, str) or not tag.strip():
            raise RefreshError(f"{name} latest release has no tag_name")
        entry["version"] = release_version(tag)
    else:
        raise RefreshError(f"{name} has no version source in components.json")

    for field in spec.get("copy_version_to") or []:
        entry[field] = entry["version"]

    if spec.get("protocol_file"):
        text = file_text(owner, repo, sha, spec["protocol_file"], fetch)
        entry["protocol_version"] = one_match(
            text, spec["protocol_pattern"], f"{name} {spec['protocol_file']}"
        )

    if spec.get("module"):
        entry["module"] = spec["module"]

    entry["role"] = spec["role"]
    return entry


def build_train(spec: dict, fetch, recorded_at: str) -> dict:
    owner = spec["owner"]
    ref = spec["ref"]
    components = spec.get("components")
    if not isinstance(components, list) or not components:
        raise RefreshError("components.json components must be a non-empty list")
    certified = {}
    for component in components:
        if not isinstance(component, dict) or "name" not in component:
            raise RefreshError(f"malformed component entry: {component!r}")
        certified[component["name"]] = component_entry(component, owner, ref, fetch)
    return {
        "schema_version": TRAIN_SCHEMA,
        "release_train": RELEASE_TRAIN,
        "published_by": PUBLISHED_BY,
        "recorded_at": recorded_at,
        "status": "certified",
        "certified": certified,
        "adoption_rule": ADOPTION_RULE,
        "note": NOTE,
    }


def comparable(train: dict) -> dict:
    """Ignore recorded_at so an unchanged head does not rewrite the file."""
    return {key: value for key, value in train.items() if key != "recorded_at"}


def render(train: dict) -> str:
    return json.dumps(train, indent=2) + "\n"


def refresh(spec: dict, current: dict | None, fetch, recorded_at: str) -> tuple[dict, bool]:
    train = build_train(spec, fetch, recorded_at)
    if current is not None and comparable(current) == comparable(train):
        return current, False
    return train, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 1 when stack-releases.json disagrees with the default branches",
    )
    args = parser.parse_args(argv)

    try:
        spec = load_json(COMPONENTS_PATH)
        current = load_json(RELEASES_PATH) if RELEASES_PATH.is_file() else None
        recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        def fetch(url: str) -> str:
            accept = (
                "application/vnd.github.raw"
                if "/contents/" in url
                else "application/vnd.github+json"
            )
            return http_get(url, token_from_env(), accept)
        train, changed = refresh(spec, current, fetch, recorded_at)
    except RefreshError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if not changed:
        print(f"OK: {RELEASES_PATH.name} already matches the default branches")
        return 0

    if args.check:
        print(f"FAIL: {RELEASES_PATH.name} is behind the default branches", file=sys.stderr)
        for name, entry in train["certified"].items():
            print(f"  - {name} {entry['version']} {entry['commit']}", file=sys.stderr)
        return 1

    RELEASES_PATH.write_text(render(train), encoding="utf-8", newline="\n")
    print(f"OK: wrote {RELEASES_PATH.name}")
    for name, entry in train["certified"].items():
        print(f"  - {name} {entry['version']} {entry['commit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
