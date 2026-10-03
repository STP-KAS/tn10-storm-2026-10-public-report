#!/usr/bin/env bash
# Re-run every derived file in this folder. Inputs are the box logs (not published raw); paths are the box paths.
set -euo pipefail
cd "$(dirname "$0")"
python3 runners_tps.py      /workspace/artifacts/stress-tests/data > /dev/null   # legs_box, runner_segments, box_5min, fee_recapture_estimate
python3 network_view.py     /workspace/kaspa-logs-tn10-n0/rusty-kaspa.log > /dev/null   # network_legs, hourly_network_vs_box
python3 block_share.py      /workspace/artifacts/stress-tests/data/host.jsonl > /dev/null
python3 block_share_sampler2.py /workspace/artifacts/kaspa-tn10/share.csv > /dev/null
python3 api_view.py         /workspace/artifacts/stress-tests/data > /dev/null
python3 desk_sender.py      /workspace/repos/tn10-storm-2026-10-analysis/desk/sender.jsonl > /dev/null
python3 mainnet_scenarios.py > /dev/null
python3 api_vs_load.py > /dev/null
python3 mempool_view.py > /dev/null
python3 make_tables.py
