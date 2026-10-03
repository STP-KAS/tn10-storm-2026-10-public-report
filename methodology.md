# Methodology

All times are CEST (UTC+2) unless marked UTC. "Box" = stp's single test machine (8 vCPU, 15 GB RAM, 126 GB disk) running TN10 node **n0** (kaspad 2.1.0), the storm runners and two CPU miners. "Desk" = Grok Build's load from stp's desk PC (`C:\Users\Fermi\...`) through public TN10 wRPC nodes.

## 1. Sources

| Source | What it records | Used for |
|---|---|---|
| Runner logs `runner1-4.out` (SMX), `p2w1-8.out` (P2W) | A `rep` JSON line every 10 s per runner: cumulative submitted, cumulative **accepted on n0's virtual chain**, cumulative fee (tKAS), mass (P2W runners only); a `final` line on exit | Box TPS, fees, mass, legs (`runners_tps.py`) |
| n0 kaspad log `rusty-kaspa.log` | `Processed N blocks … (M transactions; … mass: s/c/t)` every ~10 s | Network-wide upper bound (`network_view.py`) |
| `api-tn10.kaspa.org/transactions/count/<day>` | Unique accepted non-coinbase ("regular") txs per UTC hour, from the public indexer | Network-wide unique count (`data/sources/count-*.json`) |
| `host.jsonl` (host sampler, 15–30 s) | Blocks added on n0 by payout address and miner user agent | Block share (`block_share.py`) |
| `share.csv` (TN10 ops' independent sampler, 5 min) | n0 DAA score, cumulative box-miner "Block submitted successfully" lines, cumulative blocks submitted through n0 | Block share cross-check, only share source for L4 (`block_share_sampler2.py`) |
| `api-health-min.jsonl`, `api-mined-watch.jsonl` | `/info/health` every 120 s; newest coinbase of stp's mining address (`qzffl5…`) every 300 s | Public API behaviour (`api_view.py`) |
| Desk `sender.jsonl` (copy in the private analysis repo) | Per batch: submitted / node-acked / rejected | Desk load, ends Thu 23:23 (`desk_sender.py`) |
| `run/timeline.md`, `run/final-numbers-2026-10-02.md` | Operator event log and earlier analysis | Leg boundaries, events, cross-checks |
| rusty-kaspa `01b532e` (v2.1.0), PR #1004 | Mainnet params, mass rules, minimum relay fee | Mainnet section |
| `api.kaspa.org/info/fee-estimate`, `/info/price`, `/info/blockdag`; Kraken public ticker | Live mainnet feerate, price, DAA rate | Mainnet section (`data/sources/`) |

Raw logs are not published: they hold host names, addresses and operational detail. Only derived CSVs and the public API responses are in `data/`.

## 2. Definitions

- **Included** (headline): the runner's own count of its txs that n0 reports as accepted on the virtual chain. Unique, box only.
- **Node-acked** (desk): the node accepted `submitTransaction`. Not proof of inclusion.
- **Processed** (kaspad log): every tx in every block body n0 processed, plus coinbases. A tx in two parallel blocks counts twice. **Upper bound**, all senders. Coinbases (1 per block) are subtracted; double counting is not.
- **Regular count** (indexer): unique accepted non-coinbase txs per UTC hour. Only as good as the indexer; it froze on Fri night (README §4), so L4 hours under-count.
- **Leg**: one launch of the runners until STOP/kill/reboot. Windows (from `run/timeline.md`):
  - L1 Thu 20:35:18 → Fri 07:52:54 (RAM STOP)
  - L2 Fri 09:07:39 → 10:15:00 (box reboot)
  - L3 Fri 11:49:49 → 16:50:47 (disk STOP)
  - L4 Fri 21:52:07 → Sat 01:06:29 (disk STOP)
- **Loaded**: a second where box inclusion was ≥100 tx/s.

## 3. Throughput method (`runners_tps.py`)

1. Each runner run is a *segment*. Its cumulative `accepted` is placed on a 1-s grid by linear interpolation between `rep` lines (starting at 0 ten seconds before the first `rep`).
2. Per-second increments of all segments are summed into one box series.
3. Sliding windows of 10, 60, 300, 600 and 3,600 s give the peaks. 5-min bins give the medians and the hourly comparison.
4. Per-leg totals (included, rejected, fee) are the sum of each segment's last cumulative value. Mass per segment comes from the P2W runner's `massH`/`massF` totals (hops + funding txs) or its `mass_hop_avg`/`mass_fund_avg` fields; for SMX runners (no mass field) it is the median of Δfee ÷ (Δsubmitted × feerate) over report pairs at constant feerate. Leg average mass is weighted by included txs; average feerate = fee ÷ (included × mass).

10-s peaks are the step between two reports and depend on block timing; they are indicative only. A plain 10-s grid without interpolation gives a slightly higher L1 value (4,537).

## 4. Block share

- **Host sampler**: blocks n0 added whose coinbase pays stp's address, split by user agent (box miners vs anything else = desk), divided by all blocks n0 added in the window. Where the sampler ran with share off (blocks counted as 0 while blocks flowed) the window is "not measured". After n0's Friday restart the counter read 0, so L4 has no host-sampler share.
- **Independent sampler**: growth of the box miners' "Block submitted successfully" count ÷ growth of n0's DAA score (≈ number of TN10 blocks). DAA score is a close proxy, not an exact block count.
- **Fee recapture estimate** (TN10 side note only): the fees paid in each of six share windows (L1 SMX, L1 P2W with box miners on, L1 box miners off, L2, L3, L4) × stp's block share in that window, summed (`runners_tps.py`, `fee_recapture_estimate.csv`). This assumes stp's blocks carried an average share of the fees. It is an **inference, not verified** from coinbase amounts.

## 5. Public API flags (`api_view.py`)

- `503`: `/info/health` returned HTTP 503. Usually this came with `isSynced:false` (22 of L1's 28, all 40 in L4); a few 503s came with the indexer up to date.
- `stall_suspected` (set by the sampler): the API's `acceptedTxBlockTimeDiff` > 120 s while its kaspad backends reported synced, i.e. the indexer is behind, not the node.
- `mined_stall`: the newest coinbase shown for `qzffl5…` is older than expected given the blocks n0 saw stp mine. It depends on the host share counter, so it could not fire in L4.
- Freeze identification in L4: indexer lag growing exactly 120 s per 120-s sample from 22:23 to 23:21 (no progress at all), plus the coinbase-view lag growing 1 s per second with the same newest coinbase id shown from 22:23 to 23:18.
- Gaps (sampler not running) are listed in `data/api_gaps.csv`; nothing is inferred inside a gap.

## 5b. API episodes vs load (`api_vs_load.py`) and mempool context (`mempool_view.py`)

- **Episode windows** run from the first to the last flagged sample (stall, 503 or mined_stall) in `api_events.csv`. "Recovered" is the first later sample with HTTP 200 and lag <120 s, or newest-coinbase lag <120 s for the address view. It is bounded by the 120-s / 300-s sampling interval. Load in each window: the mean of the box 5-min bins and the mean n0 "Processed" rate (upper bound, all senders). Two Thursday-night episodes ended inside sampler gaps, so their recovery time is only bounded.
- **Earlier-test comparison:** the freeze start and the 29 Sep check come from STP-KAS/tn10-indexer-stall-2026-09 `README.md`. The upper bound on its end is the first healthy sample in the 1 Oct dry run (`artifacts/stress-tests/dryrun/api-health-min-dry.jsonl` l.2). Same endpoint and field, very different sampling density. The TN10 stream/explorer was not monitored in either test.
- **Mempool:** only n0's mempool *count* (host sampler), n0's fee estimate (`feerate.jsonl`) and kaspad's "evicted … in favor of incoming higher feerate transactions" lines. Composition and pending times were not sampled, so third-party or covenant txs cannot be singled out. No new queries were made to n0.

## 6. Mainnet formula (`mainnet_scenarios.py`)

```
cost_KAS   = txs × mass_g × feerate_sompi_per_g ÷ 1e8
txs        = tps × 3600 × hours
capacity   = 10 blocks/s × 500,000 g = 5,000,000 g/s  → max tps = 5,000,000 ÷ mass_g
fiat       = cost_KAS × Kraken last trade (USD 0.04243 @ 15:57:59 UTC, EUR 0.03778 @ 15:58:05 UTC, 3 Oct 2026)
```

- (a) **normal = 100 sompi/g**: the mainnet minimum relay fee (`DEFAULT_MINIMUM_RELAY_TRANSACTION_FEE = 100_000` sompi/kg, rusty-kaspa PR #1004), charged on the larger of compute mass and normalized transient mass, and the value `api.kaspa.org/info/fee-estimate` returned for every bucket on 3 Oct 2026 15:54 and 15:58 UTC. The older "1 sompi/g" minimum no longer applies.
- (b) **priority = 1.5 × normal = 150 sompi/g**.
- Shapes: P2W hop 644.8 g (measured average incl. funding txs) and signed 1-in-1-out P2PK 1,751.9 g (measured SMX).
- Rates: measured box peaks (1 min 4,252.8; 10 min 3,717.3) and sustained (best 60 min 2,517.6; whole-test loaded average 1,417.9).
- Durations: 0.5, 1, 2, 3, 4, 10, 12, 24 h, constant rate.
- Deliberately excluded: fee recapture through own mining, fee-market / bidding-war escalation, price impact of buying the KAS, the lane float (capital, not cost), theft risk of anyone-can-spend lanes.

## 7. Caveats

- One box, one node. Box rates are a floor for what a better-provisioned sender could do, not a network maximum.
- n0 was wiped and resynced on Sat 3 Oct; the history exists only in the logs.
- The desk log copy ends Thu 23:23. Grok Build's numbers to Fri 09:40 are quoted, not recomputed.
- Indexer counts are unreliable during the L4 freeze.
- TN10 mining share changed which fees came back to stp; it does not change gross cost, and it does not exist for a mainnet sender without hashrate.

## 8. Re-running

```
cd data && ./run_all.sh
```

The scripts take the box log paths as defaults (first argument overrides). They are standard-library Python 3 only. Re-running on the box reproduces every CSV in `data/` byte for byte (checked Sat 3 Oct 2026, ~18:20 CEST). The API samplers were still running when this was written, but every window used ends before the files' current end. `mainnet_scenarios.py` needs only `legs_box.csv` and runs anywhere.
