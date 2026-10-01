#!/usr/bin/env python3
"""Fail closed when OIO's own pins disagree with the release train it publishes.

OIO plays both roles in the stack: it publishes `stack-releases.json` (the
certified train adopters read) and it is itself an adopter, pinning what it
consumes in `stack-manifest.json`. Nothing else compares the two, so a single
edit to either file would silently desynchronise them — the exact drift this
repository exists to remove.

Exits non-zero on any disagreement in the release-train name, the component
set, or a shared version/commit field.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED_FIELDS = ("version", "commit", "cli", "module", "modules")


def load(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"FAIL: {path.name} is missing")
    except json.JSONDecodeError as exc:
        sys.exit(f"FAIL: {path.name} is not valid JSON: {exc}")
    if not isinstance(data, dict):
        sys.exit(f"FAIL: {path.name} must contain a JSON object")
    return data


def main() -> int:
    releases = load(ROOT / "stack-releases.json")
    manifest = load(ROOT / "stack-manifest.json")
    certified = releases.get("certified") or {}
    pins = manifest.get("pins") or {}
    errors: list[str] = []

    train = releases.get("release_train")
    if not train:
        errors.append("stack-releases.json is missing release_train")
    elif manifest.get("release_train") != train:
        errors.append(
            f"release_train mismatch: manifest has {manifest.get('release_train')!r}, "
            f"published train is {train!r}"
        )

    for name, pin in sorted(pins.items()):
        if name not in certified:
            errors.append(f"manifest pins {name!r}, which the release train does not certify")
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

    if errors:
        print("FAIL: stack-manifest.json disagrees with stack-releases.json")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"OK: stack-manifest.json agrees with release train {train} ({len(pins)} components)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
