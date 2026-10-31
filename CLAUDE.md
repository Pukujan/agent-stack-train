# Claude Code

Every other agent reads `AGENTS.md` by itself; Claude Code reads this file. The
import below gives Claude the same rules, and they bind here exactly as they do
there. Each component folder (`acs/`, `cgm/`, `oio/`, `pcm/`) has its own
`CLAUDE.md` that imports that folder's `AGENTS.md`.

@AGENTS.md

## GitHub is the authority

Live GitHub state decides scope, status and what is accepted: the issues, pull
requests, checks and merged `main` of
[`Pukujan/agent-stack-train`](https://github.com/Pukujan/agent-stack-train).
Read them with `gh` before you plan, resume or report, and work through them: a
branch and a pull request, never a push to `main`. Local files are projections
and caches: checkpoints, `HANDOFF.md`, any clone under `~/.cache`, and the four
frozen component repositories. When one disagrees with GitHub, GitHub wins; say
so on the owning issue.
