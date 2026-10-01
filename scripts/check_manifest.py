#!/usr/bin/env python3
"""Check one adopter's stack-manifest.json against the certified release train.

Any repository in the stack can run this in CI. It reads the adopter's manifest
and the train's stack-releases.json and fails closed on any disagreement, so a
single edit to either file cannot silently desynchronise them — the drift this
train exists to remove.

Usage:
    python scripts/check_manifest.py --manifest ../stack-manifest.json
    python scripts/check_manifest.py --manifest m.json --train-url https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json

Exit codes: 0 agreement, 1 disagreement or unreadable input.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_TRAIN_URL = (
    "https://raw.githubusercontent.com/Pukujan/agent-stack-train/main/stack-releases.json"
)
MANIFEST_SCHEMA = "agent-stack-train.stack-manifest.v1"
SHARED_FIELDS = ("version", "commit", "cli", "module", "modules")
ROOT = Path(__file__).resolve().parent.parent


def load_path(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"FAIL: {path} is missing")
    except json.JSONDecodeError as exc:
        sys.exit(f"FAIL: {path} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        sys.exit(f"FAIL: {path} must contain a JSON object")
    return data


def load_url(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        sys.exit(f"FAIL: could not read train from {url}: {exc}")
    if not isinstance(data, dict):
        sys.exit(f"FAIL: {url} must contain a JSON object")
    return data


def load_train(spec: str) -> tuple[dict, str]:
    """A spec is a URL when it has a scheme, otherwise a path (relative to CWD)."""
    if "://" in spec:
        return load_url(spec), spec
    path = Path(spec)
    return load_path(path), str(path)


def check(manifest: dict, train: dict, train_label: str) -> list[str]:
    errors: list[str] = []

    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        errors.append(f"manifest schema_version must be {MANIFEST_SCHEMA}")

    for field in ("adopter", "release_train", "source"):
        value = manifest.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"manifest is missing a non-empty {field!r}")

    certified = train.get("certified") or {}
    pins = manifest.get("pins") or {}
    if not isinstance(pins, dict) or not pins:
        errors.append("manifest pins must be a non-empty object")
        pins = {}

    train_name = train.get("release_train")
    if not train_name:
        errors.append(f"{train_label} is missing release_train")
    elif manifest.get("release_train") != train_name:
        errors.append(
            f"release_train mismatch: manifest pins {manifest.get('release_train')!r}, "
            f"the train is {train_name!r}"
        )

    for name, pin in sorted(pins.items()):
        if not isinstance(pin, dict):
            errors.append(f"pin {name!r} must be an object")
            continue
        if name not in certified:
            errors.append(f"manifest pins {name!r}, which the train does not certify")
            continue
        for field in SHARED_FIELDS:
            if field in pin and field in certified[name] and pin[field] != certified[name][field]:
                errors.append(
                    f"{name}: pinned {field}={pin[field]!r} but the train certifies "
                    f"{certified[name][field]!r}"
                )

    for name in sorted(certified):
        if name not in pins:
            errors.append(f"the train certifies {name!r} but the manifest does not pin it")

    return errors


TRAIN_SCHEMA = "agent-stack-train.stack-releases.v1"


def check_train(train: dict, label: str) -> list[str]:
    """Validate the train document alone (no adopter manifest needed)."""
    errors: list[str] = []
    if train.get("schema_version") != TRAIN_SCHEMA:
        errors.append(f"{label} schema_version must be {TRAIN_SCHEMA}")
    for field in ("release_train", "published_by"):
        value = train.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label} is missing a non-empty {field!r}")
    if train.get("status") not in {"proposed", "certified"}:
        errors.append(f"{label} status must be 'proposed' or 'certified'")
    certified = train.get("certified")
    if not isinstance(certified, dict) or not certified:
        errors.append(f"{label} certified must be a non-empty object")
    else:
        for name, entry in sorted(certified.items()):
            if not isinstance(entry, dict):
                errors.append(f"{label} certified[{name!r}] must be an object")
                continue
            if not isinstance(entry.get("version"), str) or not entry["version"].strip():
                errors.append(f"{label} certified[{name!r}] is missing a version")
            if not isinstance(entry.get("role"), str) or not entry["role"].strip():
                errors.append(f"{label} certified[{name!r}] is missing a role")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", help="path to the adopter's stack-manifest.json")
    parser.add_argument(
        "--train",
        default=str(ROOT / "stack-releases.json"),
        help="path to the train's stack-releases.json (default: this repository's copy)",
    )
    parser.add_argument("--train-url", help="fetch the train from a URL instead of --train")
    parser.add_argument(
        "--self",
        action="store_true",
        help="validate the train document alone; no adopter manifest required",
    )
    args = parser.parse_args()

    if args.train_url:
        train, label = load_url(args.train_url), args.train_url
    else:
        train, label = load_train(args.train)

    if args.self:
        errors = check_train(train, label)
        if errors:
            print(f"FAIL: {label} is not a valid release train")
            for error in errors:
                print(f"  - {error}")
            return 1
        print(f"OK: {label} is a valid release train ({len(train.get('certified', {}))} components)")
        return 0

    if not args.manifest:
        parser.error("--manifest is required unless --self is given")

    manifest = load_path(Path(args.manifest))
    errors = check(manifest, train, label)
    if errors:
        print(f"FAIL: {args.manifest} disagrees with the release train")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"OK: {manifest.get('adopter')} agrees with release train "
        f"{train.get('release_train')} ({len(manifest.get('pins', {}))} components)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
