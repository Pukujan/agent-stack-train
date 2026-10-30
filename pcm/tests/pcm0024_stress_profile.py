from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from continuity.cli import (
    checkpoint_addition,
    checkpoint_metadata,
    checkpoint_task,
    extract_marker,
    init_repo,
    initialize_document_catalog,
    marker,
    pack_task,
    render_document_index,
    search_document_catalog,
    sha256_document_bytes,
    task_new,
)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def percentile(samples: list[float], fraction: float) -> float:
    ordered = sorted(samples)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * fraction + 0.999999)))
    return ordered[index]


def run_profile(documents: int, checkpoints: int, task_documents: int, lookup_repetitions: int) -> dict[str, Any]:
    if documents < 1000 or checkpoints < 1000:
        raise ValueError("stress profile requires at least 1,000 documents and 1,000 checkpoint records")
    if not 1 <= task_documents <= documents or lookup_repetitions < 1:
        raise ValueError("task_documents must be within the document count and lookup_repetitions must be positive")

    with tempfile.TemporaryDirectory(prefix="pcm0024-stress-") as temp_name:
        root = Path(temp_name) / "repo"
        root.mkdir()
        init_repo(root, "software", "PCM-0024 stress fixture", "STR")
        task_path = task_new(
            root,
            "stress-profile",
            "Measure PCM continuation cost",
            "Exercise realistic indexed history",
            "stress-profile",
            "P1",
        )
        task_id = "STR-0001"

        current_path = root / "checkpoints" / "CURRENT.md"
        current_text = current_path.read_text(encoding="utf-8")
        current_meta = extract_marker(current_text, "current")
        if current_meta is None:
            raise RuntimeError("generated CURRENT marker is missing")
        current_meta["active_task"] = task_id
        current_meta["active_task_file"] = task_path.relative_to(root).as_posix()
        current_path.write_text(
            current_text.replace(
                marker("current", extract_marker(current_text, "current") or {}),
                marker("current", current_meta),
                1,
            ),
            encoding="utf-8",
        )

        config = json.loads((root / ".continuity" / "config.json").read_text(encoding="utf-8"))
        task_text = task_path.read_text(encoding="utf-8")
        before_handoff, after_handoff = task_text.split("## Handoff", 1)
        seed_entries = []
        seed_time = datetime(2025, 1, 1, tzinfo=UTC)
        for index in range(checkpoints):
            meta = checkpoint_metadata(
                config,
                task_id,
                "stress-seed",
                (seed_time + timedelta(seconds=index)).isoformat().replace("+00:00", "Z"),
                [f"seed event {index}"],
                ["synthetic deterministic history"],
                ["no new decision"],
                ["tests/pcm0024_stress_profile.py"],
                [],
                "continue the stress profile",
            )
            seed_entries.append(checkpoint_addition(meta, f"seed-{index:05d}"))
        task_path.write_text(
            before_handoff.rstrip() + "\n" + "\n".join(seed_entries) + "\n## Handoff" + after_handoff,
            encoding="utf-8",
        )

        tracemalloc.start()
        records: list[dict[str, Any]] = []
        docs_root = root / "docs" / "stress-fixture"
        docs_root.mkdir(parents=True)
        for index in range(documents):
            document_id = f"stress-doc-{index:05d}"
            relative = f"docs/stress-fixture/{document_id}.md"
            body = f"# Continuity stress document {index}\n\nEvidence for issue {index % 100} and task recovery.\n"
            source = root / relative
            source.write_text(body, encoding="utf-8")
            records.append(
                {
                    "id": document_id,
                    "title": f"Continuity stress document {index}",
                    "path": relative,
                    "summary": f"Evidence and task continuation record {index}.",
                    "keywords": ["continuity", "stress", f"group-{index % 100:03d}"],
                    "related": [],
                    "tasks": [task_id] if index < task_documents else [],
                    "reviewed_commit": "uncommitted",
                    "reviewed_sha256": sha256_document_bytes(source.read_bytes()),
                }
            )

        catalog_path, _ = initialize_document_catalog(root)
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["documents"] = records
        catalog_path.write_text(json.dumps(catalog, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (root / "docs" / "CONTINUITY_INDEX.md").write_text(render_document_index(root, catalog), encoding="utf-8")

        git(root, "init", "-q", "-b", "main")
        git(root, "config", "user.name", "PCM stress profile")
        git(root, "config", "user.email", "pcm-stress@example.invalid")
        git(root, "add", ".")
        git(root, "commit", "-q", "-m", "Create PCM-0024 stress fixture")

        lookup_samples: list[float] = []
        last_matches: list[tuple[int, dict[str, Any]]] = []
        for _ in range(lookup_repetitions):
            started = time.perf_counter()
            last_matches = search_document_catalog(root, catalog, "continuity group-042", task_id)
            lookup_samples.append((time.perf_counter() - started) * 1000)

        pack_started = time.perf_counter()
        pack_path = pack_task(root, task_id, None)
        pack_ms = (time.perf_counter() - pack_started) * 1000
        pack_bytes = pack_path.stat().st_size

        checkpoint_samples: list[float] = []
        base_time = datetime(2026, 1, 1, tzinfo=UTC)
        measured_appends = lookup_repetitions
        for index in range(measured_appends):
            started = time.perf_counter()
            checkpoint_task(
                root,
                task_id,
                "stress-profile",
                (base_time + timedelta(seconds=index)).isoformat().replace("+00:00", "Z"),
                [f"stress event {index}"],
                ["synthetic deterministic profile"],
                ["no new decision"],
                ["tests/pcm0024_stress_profile.py"],
                [],
                "complete the stress profile",
                request_id=f"stress-append-{index:05d}",
            )
            checkpoint_samples.append((time.perf_counter() - started) * 1000)
        _current_bytes, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        repository_bytes = sum(
            item.stat().st_size for item in root.rglob("*") if item.is_file() and ".git" not in item.parts
        )
        task_bytes = task_path.stat().st_size
        return {
            "profile": "pcm0024-stress-v1",
            "runtime": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "processor": platform.processor() or "unreported",
            },
            "fixture": {
                "indexed_documents": documents,
                "task_documents": task_documents,
                "seeded_checkpoint_records": checkpoints,
                "measured_checkpoint_appends": measured_appends,
                "lookup_repetitions": lookup_repetitions,
            },
            "results": {
                "lookup_ms": {
                    "p50": round(statistics.median(lookup_samples), 3),
                    "p95": round(percentile(lookup_samples, 0.95), 3),
                    "matches_last_run": len(last_matches),
                },
                "checkpoint_append_ms": {
                    "p50": round(statistics.median(checkpoint_samples), 3),
                    "p95": round(percentile(checkpoint_samples, 0.95), 3),
                },
                "context_pack_ms": round(pack_ms, 3),
                "context_pack_bytes": pack_bytes,
                "task_file_bytes_after_checkpoints": task_bytes,
                "repository_files_bytes": repository_bytes,
                "tracemalloc_peak_bytes": peak_memory,
            },
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproducible PCM-0024 large-repository cost profile")
    parser.add_argument("--documents", type=int, default=5000)
    parser.add_argument("--checkpoints", type=int, default=2000)
    parser.add_argument("--task-documents", type=int, default=50)
    parser.add_argument("--lookup-repetitions", type=int, default=40)
    args = parser.parse_args()
    result = run_profile(args.documents, args.checkpoints, args.task_documents, args.lookup_repetitions)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
