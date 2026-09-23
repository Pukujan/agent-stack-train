from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, env=env, check=False, capture_output=True, text=True)
    if result.returncode:
        rendered = " ".join(command)
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: {rendered}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result.stdout


def isolated_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def assert_same_tree(expected: Path, actual: Path) -> None:
    expected_files = snapshot(expected)
    actual_files = snapshot(actual)
    if expected_files.keys() != actual_files.keys():
        missing = sorted(expected_files.keys() - actual_files.keys())
        unexpected = sorted(actual_files.keys() - expected_files.keys())
        raise AssertionError(f"Generated file inventory differs; missing={missing}, unexpected={unexpected}")
    differing = sorted(path for path in expected_files if expected_files[path] != actual_files[path])
    if differing:
        raise AssertionError(f"Generated file contents differ: {differing}")


def cli_path(environment_root: Path) -> Path:
    scripts = "Scripts" if os.name == "nt" else "bin"
    executable = "continuity.exe" if os.name == "nt" else "continuity"
    return environment_root / scripts / executable


def python_path(environment_root: Path) -> Path:
    if os.name == "nt":
        return environment_root / "Scripts" / "python.exe"
    return environment_root / "bin" / "python"


def init_command(command_prefix: list[str], root: Path, profile: str) -> list[str]:
    return [
        *command_prefix,
        "init",
        "--root",
        str(root),
        "--profile",
        profile,
        "--name",
        "Package Parity Fixture",
        "--task-prefix",
        "PAR",
        "--workspace-mode",
        "managed-worktrees",
        "--github-templates",
    ]


def exercise_pcm0018_features(command_prefix: list[str], root: Path, env: dict[str, str]) -> dict[str, str]:
    """Compare source and installed behavior for retries, discovery, and focused packs."""
    fixture = Path(__file__).parent / "fixtures" / "valid-minimal"
    root.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(fixture, root)
    docs = root / "docs"
    docs.mkdir()
    (docs / "prior-plan.md").write_text("# Earlier epistemic plan\n\nFind the existing decision.\n", encoding="utf-8")
    (docs / "related-evidence.md").write_text(
        "# Related evidence\n\nThis record is a declared neighbor.\n", encoding="utf-8"
    )
    (docs / "unrelated.md").write_text("# Unrelated\n\nThis belongs to another task.\n", encoding="utf-8")

    fixture_env = env.copy()
    fixture_env.update(
        {
            "GIT_AUTHOR_DATE": "2026-09-23T00:00:00Z",
            "GIT_COMMITTER_DATE": "2026-09-23T00:00:00Z",
            "GIT_AUTHOR_NAME": "PCM package parity",
            "GIT_COMMITTER_NAME": "PCM package parity",
            "GIT_AUTHOR_EMAIL": "pcm-package-parity@example.invalid",
            "GIT_COMMITTER_EMAIL": "pcm-package-parity@example.invalid",
        }
    )
    branch = "task/PCM-0001-package-parity"
    run(["git", "init", "-q", "-b", branch], cwd=root, env=fixture_env)
    run(["git", "config", "user.name", "PCM package parity"], cwd=root, env=fixture_env)
    run(["git", "config", "user.email", "pcm-package-parity@example.invalid"], cwd=root, env=fixture_env)
    run(["git", "add", "."], cwd=root, env=fixture_env)
    run(["git", "commit", "-q", "-m", "seed PCM-0018 package parity fixture"], cwd=root, env=fixture_env)

    run([*command_prefix, "docs", "init", "--root", str(root)], cwd=root, env=fixture_env)
    document_commands = [
        [
            "prior-plan",
            "docs/prior-plan.md",
            "Earlier epistemic plan",
            "A prior decision about knowledge discovery and project continuity.",
            ["--keyword", "epistemic knowledge", "--task", "PCM-0001"],
        ],
        [
            "related-evidence",
            "docs/related-evidence.md",
            "Related evidence",
            "A neighboring record that carries provenance for the earlier plan.",
            ["--keyword", "provenance evidence", "--related", "prior-plan"],
        ],
        [
            "unrelated-record",
            "docs/unrelated.md",
            "Unrelated record",
            "An unassociated record that the task pack should leave out.",
            ["--keyword", "unrelated"],
        ],
    ]
    for document_id, path, title, summary, options in document_commands:
        run(
            [
                *command_prefix,
                "docs",
                "add",
                document_id,
                "--root",
                str(root),
                "--path",
                path,
                "--title",
                title,
                "--summary",
                summary,
                *options,
            ],
            cwd=root,
            env=fixture_env,
        )
    run(["git", "add", "."], cwd=root, env=fixture_env)
    run(["git", "commit", "-q", "-m", "register PCM-0018 parity documents"], cwd=root, env=fixture_env)

    remote = root.parent / "remote.git"
    run(["git", "init", "-q", "--bare", str(remote)], cwd=root.parent, env=fixture_env)
    run(["git", "remote", "add", "origin", "../remote.git"], cwd=root, env=fixture_env)
    run(["git", "push", "-q", "--set-upstream", "origin", "HEAD"], cwd=root, env=fixture_env)
    run(["git", "fetch", "-q", "origin"], cwd=root, env=fixture_env)
    run(["git", "remote", "set-head", "origin", branch], cwd=root, env=fixture_env)

    lookup = run(
        [*command_prefix, "docs", "find", "epistemic knowledge", "--root", str(root), "--task", "PCM-0001"],
        cwd=root,
        env=fixture_env,
    )
    if "MATCH prior-plan [CURRENT]" not in lookup or "RELATED related-evidence [CURRENT]" not in lookup:
        raise AssertionError(f"Document lookup missed the prior record or its neighbor:\n{lookup}")
    if "unrelated-record" in lookup:
        raise AssertionError(f"Task-scoped document lookup included an unrelated record:\n{lookup}")

    checkpoint_args = [
        *command_prefix,
        "checkpoint",
        "PCM-0001",
        "--root",
        str(root),
        "--agent",
        "package-parity",
        "--request-id",
        "package-retry-001",
        "--time",
        "2026-09-23T00:00:00Z",
        "--completed",
        "fixture task completed",
        "--evidence",
        "installed command passed",
        "--decision",
        "one request produces one event",
        "--changed",
        "docs/prior-plan.md",
        "--next",
        "run validation",
    ]
    first = run(checkpoint_args, cwd=root, env=fixture_env)
    first_commit = run(["git", "rev-parse", "HEAD"], cwd=root, env=fixture_env).strip()
    second = run(checkpoint_args, cwd=root, env=fixture_env)
    second_commit = run(["git", "rev-parse", "HEAD"], cwd=root, env=fixture_env).strip()
    task_text = (root / "tasks" / "TASK-PCM-0001-example.md").read_text(encoding="utf-8")
    if "REQUEST_ID: package-retry-001" not in first or "REQUEST_ID: package-retry-001" not in second:
        raise AssertionError("Checkpoint command did not expose the stable retry ID before mutation")
    if first_commit != second_commit or task_text.count('"request_id":"package-retry-001"') != 1:
        raise AssertionError("Checkpoint retry created another commit or event")

    run([*command_prefix, "validate", "--root", str(root)], cwd=root, env=fixture_env)
    run([*command_prefix, "docs", "render", "--root", str(root), "--check"], cwd=root, env=fixture_env)
    run([*command_prefix, "pack", "PCM-0001", "--root", str(root)], cwd=root, env=fixture_env)
    pack = (root / ".continuity" / "packs" / "PCM-0001.md").read_text(encoding="utf-8")
    if "docs/prior-plan.md" not in pack or "docs/related-evidence.md" not in pack:
        raise AssertionError("Task context pack omitted a task-associated document or its neighbor")
    if "docs/unrelated.md" in pack or "run validation" not in pack:
        raise AssertionError("Task context pack included unrelated material or omitted its exact next action")
    normalized_pack = re.sub(r'"generated_at":"[^"]+"', '"generated_at":"<generated>"', pack)

    commit_count = run(["git", "rev-list", "--count", "HEAD"], cwd=root, env=fixture_env).strip()
    if commit_count != "3":
        raise AssertionError(f"Expected exactly three fixture commits after one checkpoint, found {commit_count}")
    return {
        "catalog": (root / ".continuity" / "documents.json").read_text(encoding="utf-8"),
        "index": (docs / "CONTINUITY_INDEX.md").read_text(encoding="utf-8"),
        "task": task_text,
        "lookup": lookup,
        "pack": normalized_pack,
        "head": second_commit,
        "commit_count": commit_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and install PCM artifacts outside the checkout.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    source_root = args.root.resolve()
    if not (source_root / "pyproject.toml").is_file():
        parser.error(f"--root does not contain pyproject.toml: {source_root}")

    with tempfile.TemporaryDirectory(prefix="pcm-package-parity-") as temp_name:
        temp_root = Path(temp_name).resolve()
        artifacts = temp_root / "artifacts"
        artifacts.mkdir()
        isolated_env = isolated_environment()
        build_source = temp_root / "build-source"
        build_source.mkdir()
        shutil.copy2(source_root / "pyproject.toml", build_source / "pyproject.toml")
        shutil.copytree(
            source_root / "src",
            build_source / "src",
            ignore=shutil.ignore_patterns("*.egg-info", "__pycache__"),
        )

        run(
            [sys.executable, "-m", "build", "--wheel", "--sdist", "--outdir", str(artifacts), str(build_source)],
            cwd=temp_root,
            env=isolated_env,
        )
        wheels = list(artifacts.glob("*.whl"))
        sdists = list(artifacts.glob("*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1:
            raise AssertionError(f"Expected exactly one wheel and sdist; found wheels={wheels}, sdists={sdists}")

        source_env = isolated_env.copy()
        source_env["PYTHONPATH"] = str(source_root / "src")
        expected: dict[str, Path] = {}
        for profile in ("minimal", "software"):
            expected_root = temp_root / f"source-{profile}"
            run(
                init_command([sys.executable, "-m", "continuity"], expected_root, profile),
                cwd=temp_root,
                env=source_env,
            )
            run(
                [sys.executable, "-m", "continuity", "validate", "--root", str(expected_root)],
                cwd=temp_root,
                env=source_env,
            )
            expected[profile] = expected_root

        expected_features = exercise_pcm0018_features(
            [sys.executable, "-m", "continuity"], temp_root / "source-features" / "pcm018", source_env
        )

        for artifact in (wheels[0], sdists[0]):
            environment_root = temp_root / f"venv-{artifact.suffix.removeprefix('.')}"
            venv.EnvBuilder(with_pip=True).create(environment_root)
            environment_python = python_path(environment_root)
            run(
                [
                    str(environment_python),
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-input",
                    str(artifact),
                ],
                cwd=temp_root,
                env=isolated_env,
            )

            version_info = run(
                [
                    str(environment_python),
                    "-c",
                    (
                        "from importlib.metadata import version; import continuity; "
                        "print(version('project-continuity')); print(continuity.__version__)"
                    ),
                ],
                cwd=temp_root,
                env=isolated_env,
            ).splitlines()
            cli = cli_path(environment_root)
            if not cli.is_file():
                raise AssertionError(f"Installed console script is missing: {cli}")
            cli_version = run([str(cli), "--version"], cwd=temp_root, env=isolated_env).strip()
            expected_cli_version = f"continuity {version_info[0]}" if version_info else ""
            if len(version_info) != 2 or version_info[0] != version_info[1] or cli_version != expected_cli_version:
                raise AssertionError(
                    f"Installed version values disagree: metadata/module={version_info}, CLI={cli_version!r}"
                )

            for profile in ("minimal", "software"):
                actual_root = temp_root / f"{artifact.suffix.removeprefix('.')}" / profile
                run(init_command([str(cli)], actual_root, profile), cwd=temp_root, env=isolated_env)
                run([str(cli), "validate", "--root", str(actual_root)], cwd=temp_root, env=isolated_env)
                assert_same_tree(expected[profile], actual_root)
                print(f"PASS {artifact.name} on Python {sys.version_info.major}.{sys.version_info.minor}: {profile}")

            actual_features = exercise_pcm0018_features(
                [str(cli)],
                temp_root / f"{artifact.suffix.removeprefix('.')}" / "features" / "pcm018",
                isolated_env,
            )
            if actual_features != expected_features:
                differing = sorted(
                    key for key in expected_features if expected_features[key] != actual_features.get(key)
                )
                raise AssertionError(f"Installed PCM-0018 feature behavior differs from source: {differing}")
            print(
                f"PASS {artifact.name} on Python {sys.version_info.major}.{sys.version_info.minor}: PCM-0018 features"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
