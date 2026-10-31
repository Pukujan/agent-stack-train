#!/usr/bin/env python3
"""Copy the stack's memory files from git into its Octo workspace (#60).

Git is the record and Octo is the index (#52): agents search Octo to recall
history without loading it at startup, then read the file in git before acting
on it. So the index holds exactly what is on this checkout, normally ``main``:

* a memory file (CURRENT.md, the checkpoint archive, task files, PROJECT.md,
  research notes) that is new or changed becomes a new version of the Octo
  document titled with its path;
* an unchanged file is skipped without an upload, by comparing its SHA-256 with
  the latest version Octo holds;
* a document whose file is gone from git is deleted, so nothing exists only in
  Octo. Only titles that look like memory paths are touched.

Octo indexes while the request waits, and Cloudflare gives up after 100
seconds (HTTP 524) on large files even though Octo finishes them. A timeout is
therefore read as "still indexing": the script waits for the version to show
chunks instead of retrying, and a retry would be harmless anyway because Octo
ignores identical content. A version that still has no chunks after
STUCK_AFTER is deleted and sent again.

It reads the workspace key from OCTO_STACK_WS_KEY and never prints it. Without
the key it reports a skip and exits 0, so forks and local runs pass.

Usage:
    python scripts/octo_sync.py              # sync this checkout
    python scripts/octo_sync.py --dry-run    # print the plan, write nothing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("OCTO_URL", "https://octodb.design-bakery.com/api")
KEY_ENV = "OCTO_STACK_WS_KEY"

# A memory file sits at the repository root or one component folder down.
MEMORY_PATH = re.compile(
    r"^(?:[a-z][a-z0-9-]*/)?"
    r"(?:checkpoints/CURRENT\.md|checkpoints/history/[^/]+\.md|tasks/TASK-[^/]+\.md"
    r"|PROJECT\.md|docs/research/[^/]+\.md)$"
)
GATEWAY_TIMEOUTS = {502, 504, 522, 524}
STUCK_AFTER = timedelta(minutes=15)
WAIT_FOR_INDEX = timedelta(minutes=12)


def is_memory_path(path: str) -> bool:
    return MEMORY_PATH.match(path) is not None


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class Remote:
    """The latest version Octo holds for one document."""
    document_id: str
    content_hash: str | None
    chunks: int
    created_at: datetime | None


@dataclass(frozen=True)
class Step:
    action: str  # "skip", "ingest", "reingest" or "delete"
    path: str
    reason: str
    document_id: str | None = None


def plan(local: dict[str, str], remote: dict[str, Remote], now: datetime) -> list[Step]:
    """What to do for each memory path, from local hashes and Octo's latest versions. Pure."""
    steps = []
    for path in sorted(local):
        doc = remote.get(path)
        if doc is None:
            steps.append(Step("ingest", path, "new"))
        elif doc.content_hash != local[path]:
            steps.append(Step("ingest", path, "changed", doc.document_id))
        elif doc.chunks > 0:
            steps.append(Step("skip", path, "unchanged", doc.document_id))
        elif doc.created_at and now - doc.created_at > STUCK_AFTER:
            steps.append(Step("reingest", path, "indexed with no chunks", doc.document_id))
        else:
            steps.append(Step("skip", path, "still indexing", doc.document_id))
    for path in sorted(set(remote) - set(local)):
        if is_memory_path(path):
            steps.append(Step("delete", path, "gone from git", remote[path].document_id))
    return steps


class Octo:
    def __init__(self, key: str, base: str = BASE):
        self.key, self.base = key, base.rstrip("/")
        self.workspace = self.call("GET", "/capabilities")["token"]["workspaceId"]

    def call(self, method: str, path: str, body: dict | None = None, params: dict | None = None,
             timeout: int = 180):
        url = self.base + path + ("?" + urllib.parse.urlencode(params) if params else "")
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(url, data=data, method=method, headers={
            "Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
            "User-Agent": "agent-stack-train-octo-sync"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode())

    def documents(self, only: str | None = None) -> dict[str, Remote]:
        listed = self.call("GET", "/rag/documents", params={"workspaceId": self.workspace})
        return {d["title"]: self.latest(d["documentId"]) for d in listed
                if is_memory_path(d["title"]) and only in (None, d["title"])}

    def latest(self, document_id: str) -> Remote:
        doc = self.call("GET", f"/rag/documents/{document_id}", params={"workspaceId": self.workspace})
        versions = sorted(doc.get("versions", []), key=lambda v: v["versionNumber"])
        if not versions:
            return Remote(document_id, None, 0, None)
        v = versions[-1]
        created = datetime.fromisoformat(v["createdAt"].replace("Z", "+00:00")) if v.get("createdAt") else None
        return Remote(document_id, v["contentHash"], v["chunkCount"], created)

    def ingest(self, path: str, text: str) -> None:
        self.call("POST", "/rag/documents", {"workspaceId": self.workspace, "title": path,
                                             "text": text, "mimeType": "text/markdown"}, timeout=600)

    def delete(self, document_id: str) -> None:
        self.call("DELETE", f"/rag/documents/{document_id}", params={"workspaceId": self.workspace})


def send(octo, path: str, text: str, want: str, sleep=time.sleep, clock=time.monotonic) -> str:
    """Ingest one file; on a gateway timeout, wait for Octo to finish indexing it."""
    try:
        octo.ingest(path, text)
        return "indexed"
    except urllib.error.HTTPError as error:
        if error.code not in GATEWAY_TIMEOUTS:
            raise
    except TimeoutError:
        pass
    deadline = clock() + WAIT_FOR_INDEX.total_seconds()
    while clock() < deadline:
        sleep(20)
        doc = octo.documents(only=path).get(path)
        if doc and doc.content_hash == want and doc.chunks > 0:
            return "indexed after a gateway timeout"
    raise TimeoutError(f"{path}: Octo had not finished indexing after {WAIT_FOR_INDEX}")


def memory_files(root: Path) -> dict[str, bytes]:
    tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True,
                             check=True).stdout.split("\n")
    files = {}
    for path in tracked:
        if is_memory_path(path):
            data = (root / path).read_bytes()
            if data.strip():
                files[path] = data
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true", help="print the plan and write nothing")
    args = parser.parse_args(argv)

    key = os.environ.get(KEY_ENV)
    if not key:
        print(f"Skipped: {KEY_ENV} is not set, so nothing was synced to Octo.")
        return 0
    files = memory_files(ROOT)
    octo = Octo(key)
    steps = plan({p: sha256(d) for p, d in files.items()}, octo.documents(), datetime.now(timezone.utc))

    failed = 0
    for step in steps:
        line = f"{step.action:8} {step.path} ({step.reason})"
        if args.dry_run or step.action == "skip":
            print(line)
            continue
        try:
            if step.action in {"delete", "reingest"}:
                octo.delete(step.document_id)
            if step.action != "delete":
                line += ": " + send(octo, step.path, files[step.path].decode("utf-8"), sha256(files[step.path]))
            print(line, flush=True)
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            failed += 1
            print(f"FAILED   {step.path}: {error}", flush=True)

    counts = {a: sum(s.action == a for s in steps) for a in ("ingest", "reingest", "delete", "skip")}
    print(f"\n{len(files)} memory files; " + ", ".join(f"{n} {a}" for a, n in counts.items())
          + (f"; {failed} failed" if failed else "") + (" (dry run)" if args.dry_run else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
