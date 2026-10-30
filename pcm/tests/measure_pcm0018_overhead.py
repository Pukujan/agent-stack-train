from __future__ import annotations

import contextlib
import io
import json
import math
import platform
import shutil
import sys
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

from continuity.cli import checkpoint_task, initialize_document_catalog, main, upsert_document

FIXTURE = Path(__file__).parent / "fixtures" / "valid-minimal"


def percentile(samples: list[float], fraction: float) -> float:
    ordered = sorted(samples)
    return ordered[math.ceil(fraction * len(ordered)) - 1]


def measure_checkpoints(root: Path, count: int = 100) -> dict[str, float | int]:
    shutil.copytree(FIXTURE, root)
    task = root / "tasks" / "TASK-PCM-0001-example.md"
    initial_size = task.stat().st_size
    durations: list[float] = []
    base_time = datetime(2026, 9, 23, tzinfo=UTC)
    for index in range(count):
        started = time.perf_counter()
        checkpoint_task(
            root,
            "PCM-0001",
            "measurement",
            (base_time + timedelta(seconds=index)).isoformat().replace("+00:00", "Z"),
            ["measured fixture event"],
            ["synthetic reproducible measurement"],
            ["no new decision"],
            ["tests/measure_pcm0018_overhead.py"],
            [],
            "finish measurement",
            request_id=f"measurement-{index:03d}",
        )
        durations.append(time.perf_counter() - started)

    content = task.read_bytes()
    operation_line = next(line for line in content.splitlines() if b"continuity:checkpoint-operation" in line)
    return {
        "events": count,
        "append_p50_ms": round(1000 * percentile(durations, 0.50), 3),
        "append_p95_ms": round(1000 * percentile(durations, 0.95), 3),
        "task_bytes_before": initial_size,
        "task_bytes_after": len(content),
        "bytes_per_event_amortized": round((len(content) - initial_size) / count, 1),
        "operation_marker_bytes": len(operation_line),
    }


def measure_document_lookup(root: Path, record_count: int = 12, repeats: int = 25) -> dict[str, float | int]:
    shutil.copytree(FIXTURE, root)
    docs = root / "docs"
    docs.mkdir()
    for index in range(record_count):
        path = f"docs/record-{index:02d}.md"
        (root / path).write_text(f"# Continuity record {index}\n\nDiscovery fixture.\n", encoding="utf-8")
    initialize_document_catalog(root)
    for index in range(record_count):
        upsert_document(
            root,
            f"record-{index:02d}",
            f"docs/record-{index:02d}.md",
            f"Continuity record {index}",
            "A bounded discovery record used for cost measurement.",
            ["continuity", "discovery"],
            [],
            ["PCM-0001"],
        )

    durations: list[float] = []
    for _ in range(repeats):
        started = time.perf_counter()
        with contextlib.redirect_stdout(io.StringIO()):
            result = main(["docs", "find", "continuity discovery", "--root", str(root), "--task", "PCM-0001"])
        durations.append(time.perf_counter() - started)
        if result != 0:
            raise RuntimeError("document lookup measurement fixture did not return matches")
    return {
        "records": record_count,
        "lookups": repeats,
        "lookup_p50_ms": round(1000 * percentile(durations, 0.50), 3),
        "lookup_p95_ms": round(1000 * percentile(durations, 0.95), 3),
        "catalog_bytes": (root / ".continuity" / "documents.json").stat().st_size,
        "human_index_bytes": (docs / "CONTINUITY_INDEX.md").stat().st_size,
    }


def main_measurement() -> int:
    with tempfile.TemporaryDirectory(prefix="pcm0018-cost-") as temporary:
        root = Path(temporary)
        checkpoint = measure_checkpoints(root / "checkpoint-fixture")
        documents = measure_document_lookup(root / "document-fixture")
    print(
        json.dumps(
            {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
                "checkpoint": checkpoint,
                "document_lookup": documents,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main_measurement())
