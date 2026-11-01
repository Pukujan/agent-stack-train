#!/usr/bin/env bash
# Run TLC on every configuration and compare each result with the one expected.
#
#   TLA2TOOLS=/path/to/tla2tools.jar verification/lifecycle/check.sh
#
# TLC's exit code says what it found: 0 nothing, 12 an invariant broken,
# 13 a temporal property (such as "eventually closed") broken. Anything else
# is an error in the spec or the run, and fails this script.
set -u
cd "$(dirname "$0")"
jar=${TLA2TOOLS:?set TLA2TOOLS to the path of tla2tools.jar}

# config            expected exit  meaning
expectations=(
  "Lifecycle        0   real design: (b) closes and (c) never reopens hold"
  "StopReal         12  real design: (a) is broken (finding, see README)"
  "StopRetryOnly    12  the stop_hook_active bypass alone breaks (a)"
  "BranchSwitchOnly 12  the checked-out-branch gap alone breaks (a)"
  "StopFixed        0   proposed guard: (a), (b) and (c) hold"
  "GuardOff         12  negative control: ACS_GUARD=off breaks (a)"
  "SweepOff         13  negative control: sweep apply off breaks (b)"
)

failed=0
for row in "${expectations[@]}"; do
  read -r cfg want meaning <<<"$row"
  out=$(java -XX:+UseParallelGC -cp "$jar" tlc2.TLC -workers auto -cleanup \
        -metadir "${TMPDIR:-/tmp}/tlc-$cfg" -config "$cfg.cfg" Lifecycle.tla 2>&1)
  got=$?
  states=$(grep -Eo '[0-9,]+ distinct states found' <<<"$out" | tail -1)
  broken=$(grep -Eo '(Invariant|Temporal properties) [A-Za-z ]*(is|were) violated' <<<"$out" | head -1)
  if [ "$got" = "$want" ]; then
    echo "ok   $cfg: exit $got, ${states:-no state count}${broken:+, $broken} -- $meaning"
  else
    echo "FAIL $cfg: exit $got, expected $want -- $meaning"
    echo "$out" | tail -40
    failed=1
  fi
done
exit $failed
