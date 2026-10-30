# PCM-0046 arm harness (pre-registered execution aids)

- `PCM-0046-arm-launcher.sh` prints the exact participant prompts (arms spawned via the agent task tool, one fresh subagent per arm; bundles staged per the plan).
- `PCM-0046-arm-scorer.py` grades stored artifacts under /tmp/pcm0046-arms/results/ with the merged tests/traversal_scorer.py. Rescoring is a pure function over stored artifacts; it never reruns arms.
- Bundles exclude rubric.json and all *_expected.json (hidden rubric rule).
