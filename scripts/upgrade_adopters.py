#!/usr/bin/env python3
"""Open an upgrade pull request in each adopter that is behind the certified stack.

The train certifies one stack commit (``agent-stack-train`` in
stack-releases.json). For every repository in adopters.json this reads, from
GitHub, the adopter's stack-manifest.json and .oio/install-manifest.json on its
default branch, and decides:

* skip, when the adopter is not on the one-checkout stack yet (its manifest
  pins more than ``agent-stack-train``, or pins it to a fixed commit);
* skip, when it already has the certified commit installed;
* skip, when an open pull request already installs the certified commit;
* skip, when its installed commit is not an ancestor of the certified one;
* otherwise upgrade: clone it, rerun ACS's installer from the certified commit
  with ``--force`` (which keeps seats and history), and push the result to the
  branch ``agent-stack/upgrade`` with one pull request, opened or updated.

Nothing merges here. The adopter's own checks and merge rules decide.

Without ``--apply`` it only prints the decisions. With ``--apply`` it needs a
GitHub token in GH_TOKEN that can push to the adopters, open pull requests and
change workflow files: GitHub refuses a push that edits .github/workflows/
from a token without the ``workflow`` scope, and a pull request opened with a
workflow's own token starts no checks.

Usage:
    python scripts/upgrade_adopters.py                 # report only
    python scripts/upgrade_adopters.py --apply --only Pukujan/design-bakery
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STACK = "agent-stack-train"
BRANCH = "agent-stack/upgrade"
INSTALLER = "acs/modules/coordination/multi-agent-hotload/v0.1.0/scripts/acs_install.py"


@dataclass
class Adopter:
    repository: str
    manifest: dict | None
    installed_ref: str | None
    open_prs: dict[int, str | None]  # PR number -> oio_ref installed on its head


@dataclass
class Decision:
    action: str  # "upgrade" or "skip"
    reason: str


def decide(adopter: Adopter, certified: str, is_ancestor) -> Decision:
    """Pure decision for one adopter; ``is_ancestor(old, new)`` asks git."""
    pins = (adopter.manifest or {}).get("pins")
    if pins != {STACK: {}}:
        return Decision("skip", "not on the one-checkout stack (its manifest does not pin agent-stack-train alone, unpinned)")
    if adopter.installed_ref == certified:
        return Decision("skip", "up to date")
    for number, ref in sorted(adopter.open_prs.items()):
        if ref == certified:
            return Decision("skip", f"open pull request #{number} already installs it")
    if not adopter.installed_ref:
        return Decision("skip", "no installed stack commit (.oio/install-manifest.json has no oio_ref)")
    if not is_ancestor(adopter.installed_ref, certified):
        return Decision("skip", f"installed {adopter.installed_ref[:7]} is not behind the certified commit")
    return Decision("upgrade", f"installed {adopter.installed_ref[:7]} is behind")


def run(argv: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, check=check, capture_output=True, text=True)


def gh_json(*args: str):
    proc = run(["gh", *args], check=False)
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout or "null")


def read_file(repository: str, path: str, ref: str) -> dict | None:
    data = gh_json("api", f"repos/{repository}/contents/{path}?ref={ref}")
    if not isinstance(data, dict) or "content" not in data:
        return None
    try:
        return json.loads(base64.b64decode(data["content"]).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def installed_ref(repository: str, ref: str) -> str | None:
    return (read_file(repository, ".oio/install-manifest.json", ref) or {}).get("oio_ref")


def load_adopter(repository: str) -> Adopter:
    info = gh_json("api", f"repos/{repository}") or {}
    default = info.get("default_branch", "main")
    prs = gh_json("pr", "list", "-R", repository, "--state", "open", "--json", "number,headRefName,isCrossRepository") or []
    return Adopter(
        repository=repository,
        manifest=read_file(repository, "stack-manifest.json", default),
        installed_ref=installed_ref(repository, default),
        open_prs={pr["number"]: installed_ref(repository, pr["headRefName"]) for pr in prs if not pr.get("isCrossRepository")},
    )


def git_is_ancestor(stack_root: Path):
    def is_ancestor(old: str, new: str) -> bool:
        return run(["git", "-C", str(stack_root), "merge-base", "--is-ancestor", old, new], check=False).returncode == 0
    return is_ancestor


# The issue that owns adopter upgrades: the one-repo move and its release train.
UPGRADE_ISSUE = "Pukujan/agent-stack-train#21"


def bump_workflows(clone: Path, old: str, new: str) -> list[str]:
    """Move the old installed commit to the new one in the adopter's own workflows (#42).

    The installer rewrites the files it owns; an adopter's hand-written workflow
    that checks the stack out at a fixed commit would otherwise validate the old
    stack. Only the full 40-character commit is replaced, so no other text matches.
    """
    changed = []
    for path in sorted((clone / ".github" / "workflows").glob("*.y*ml")):
        text = path.read_text(encoding="utf-8")
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")
            changed.append(path.relative_to(clone).as_posix())
    return changed


def pr_body(version: str, commit: str, old: str, leftovers: list[str], log_tail: str, bumped: list[str] | None = None) -> str:
    stack = "https://github.com/Pukujan/agent-stack-train"
    lines = [
        f"This repository runs agent stack `{old[:7]}`, but the release train now certifies {version} "
        f"([`{commit[:7]}`]({stack}/commit/{commit})), so its checks and Claude Code hooks enforce an older set of rules "
        f"than the stack promises. See the [release notes]({stack}/releases/tag/v{version}) for what changed.",
        "",
        "## Change and scope",
        "",
        "- Reruns ACS's installer from that commit with `--force`, as a person would. It keeps the seats and boss history in "
        "`.coord/assignment.json`, moves the pins, and refreshes OIO's managed files, the close callers, `CLAUDE.md`'s stack "
        "region and the guard hooks in `.claude/`.",
    ]
    if bumped:
        lines.append("- Moves the old commit to the new one in this repository's own workflows, which the installer does not own: "
                     + ", ".join(f"`{p}`" for p in bumped) + ".")
    lines += [
        "",
        "## What stays unchanged",
        "",
        "Product code, this repository's own text in `CLAUDE.md` and `AGENTS.md` outside the stack's marked regions, its own hooks "
        "in `.claude/settings.json`, and its merge rules. This pull request never merges itself: this repository's checks decide.",
        "",
        "## Verification",
        "",
        "This pull request's checks validate the installed files against the certified commit. The installer's own output is below.",
    ]
    if leftovers:
        lines += ["", f"These tracked files still name the old commit `{old[:7]}` and were not rewritten. Check them before merging:", ""]
        lines += [f"- `{path}`" for path in leftovers]
    lines += [
        "",
        "<details><summary>Installer output</summary>", "", "```", log_tail, "```", "", "</details>",
        "",
        "## Evidence and provenance",
        "",
        f"- Opened by agent-stack-train's `upgrade-adopters` workflow from `{commit[:7]}`. Parent: {UPGRADE_ISSUE}.",
        "- Next action: merge when the checks pass; the bot reopens it if the train moves again first.",
        "",
        # Every pull request names its owning issue, and OIO's check fails one that does not (#37).
        f"Refs {UPGRADE_ISSUE}",
    ]
    return "\n".join(lines) + "\n"


def upgrade(repository: str, stack_root: Path, version: str, commit: str, old: str, workdir: Path) -> str:
    """Install the certified commit into a fresh clone and open or update the pull request."""
    stack = workdir / "stack"
    if not stack.exists():
        run(["git", "-C", str(stack_root), "worktree", "add", "--detach", str(stack), commit])
    clone = workdir / repository.replace("/", "__")
    run(["gh", "repo", "clone", repository, str(clone), "--", "--depth", "1", "--quiet"])
    run(["git", "checkout", "-q", "-B", BRANCH], cwd=clone)
    proc = run(
        [sys.executable, str(stack / INSTALLER), "--adopter-root", str(clone), "--stack-root", str(stack),
         "--project-id", repository, "--force"],
        check=False,
    )
    log_tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-15:])
    if proc.returncode != 0:
        raise RuntimeError(f"installer failed:\n{log_tail}")
    if not run(["git", "status", "--porcelain"], cwd=clone).stdout.strip():
        return "installer changed nothing"
    bumped = bump_workflows(clone, old, commit)
    leftovers = sorted(set(run(["git", "grep", "-l", "-I", "-e", old, "-e", old[:7]], cwd=clone, check=False).stdout.split()))
    name = os.environ.get("STACK_UPGRADE_GIT_NAME", "agent-stack-train upgrader")
    email = os.environ.get("STACK_UPGRADE_GIT_EMAIL", "noreply@github.com")
    title = f"chore(stack): upgrade agent stack to {version}"
    run(["git", "add", "-A"], cwd=clone)
    run(["git", "-c", f"user.name={name}", "-c", f"user.email={email}", "commit", "-q", "-m",
         f"{title}\n\nRerun ACS's installer from Pukujan/agent-stack-train at {commit}."], cwd=clone)
    run(["git", "push", "-q", "--force", "origin", BRANCH], cwd=clone)
    body = workdir / f"{clone.name}.md"
    body.write_text(pr_body(version, commit, old, leftovers, log_tail, bumped), encoding="utf-8")
    existing = gh_json("pr", "list", "-R", repository, "--head", BRANCH, "--state", "open", "--json", "url") or []
    if existing:
        run(["gh", "pr", "edit", existing[0]["url"], "--title", title, "--body-file", str(body)])
        return f"updated {existing[0]['url']}"
    url = run(["gh", "pr", "create", "-R", repository, "--head", BRANCH, "--title", title, "--body-file", str(body)], cwd=clone).stdout.strip()
    return f"opened {url}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--adopters", default=str(ROOT / "adopters.json"))
    parser.add_argument("--train", default=str(ROOT / "stack-releases.json"))
    parser.add_argument("--stack-root", default=str(ROOT), help="a full-history checkout of agent-stack-train")
    parser.add_argument("--only", help="one OWNER/REPOSITORY from the list")
    parser.add_argument("--apply", action="store_true", help="push branches and open pull requests")
    args = parser.parse_args()

    certified = json.loads(Path(args.train).read_text(encoding="utf-8"))["certified"][STACK]
    version, commit = certified["version"], certified["commit"]
    repositories = json.loads(Path(args.adopters).read_text(encoding="utf-8"))["repositories"]
    if args.only:
        repositories = [r for r in repositories if r == args.only]
        if not repositories:
            parser.error(f"{args.only} is not in {args.adopters}")
    stack_root = Path(args.stack_root)
    is_ancestor = git_is_ancestor(stack_root)
    print(f"certified: {STACK} {version} at {commit[:7]}; {'applying' if args.apply else 'report only'}")

    failures = 0
    with tempfile.TemporaryDirectory(prefix="stack-upgrade-") as tmp:
        workdir = Path(tmp)
        try:
            for repository in repositories:
                adopter = load_adopter(repository)
                decision = decide(adopter, commit, is_ancestor)
                outcome = decision.reason
                if decision.action == "upgrade":
                    if args.apply:
                        try:
                            outcome += f": {upgrade(repository, stack_root, version, commit, adopter.installed_ref, workdir)}"
                        except (RuntimeError, subprocess.CalledProcessError) as exc:
                            failures += 1
                            detail = exc.stderr if isinstance(exc, subprocess.CalledProcessError) else str(exc)
                            outcome += f": FAILED: {detail.strip()}"
                    else:
                        outcome += ": would upgrade"
                print(f"{repository}: {decision.action}: {outcome}")
        finally:
            if (workdir / "stack").exists():
                run(["git", "-C", str(stack_root), "worktree", "remove", "--force", str(workdir / "stack")], check=False)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
