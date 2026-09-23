from __future__ import annotations

import argparse
import os
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

        run(
            [sys.executable, "-m", "build", "--wheel", "--sdist", "--outdir", str(artifacts), str(source_root)],
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
