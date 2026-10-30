# Agent Operating Contract

These rules apply everywhere in this repository. Each component folder has its own `AGENTS.md` with the rules for that component; read it before you edit inside the folder. Where the two disagree, the folder's file wins inside its folder.

## Start

1. Read [`README.md`](README.md) for the layout and where the move stands.
2. Pick the one folder your task belongs to and read its `AGENTS.md`, `PROJECT.md` and current checkpoint.
3. A change that spans folders needs a task or issue that names every folder it touches.

## Rules

- **One folder per change** where you can. Keep each component's tests passing from inside its folder.
- **No version pins in prose.** Point at `stack-releases.json`. `scripts/check_prose_pins.py` fails a root document that restates a current component version or commit.
- **Issues follow OIO.** File with the form in [`oio/`](oio/). A filed issue is a proposal, not a mandate. Prepare a draft locally; submit it only when a human names the destination and the action.
- **Pull requests only.** Nothing is pushed to `main` directly. The `gates` check must pass.
- **The old repositories are frozen.** Don't open pull requests there. A change that has to reach adopters before the switch in step 3 of #21 needs the owner's direction.
- **License.** Everything here is FSL-1.1-ALv2. Don't add a per-folder license.
- **Secrets.** Never commit a credential. CI scans the tracked tree.
