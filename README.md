# TN10 stress test, 1–3 Oct 2026: public report

**Kaspa Testnet-10 (TN10) only. Nothing in this test touched mainnet.** The mainnet section is arithmetic on the measured TN10 numbers.

Written Sat 3 Oct 2026, about 18:00 CEST, by Grok Bot on stp's box, from the box's own logs. **All times are CEST (UTC+2).** Every number names the file or script it came from. Anything worked out rather than read is marked *(inference)*. Anything that could not be checked is marked **UNVERIFIED**. The scripts and the small derived CSVs are in [`data/`](data/). How each number was computed is in [`methodology.md`](methodology.md).

## Summary

| | Value | Source |
|---|---:|---|
| Box transactions included on the virtual chain, 4 legs | **58,905,910** | `data/legs_box.csv` |
| Rejected by the node | 152 (all one resume glitch, Fri 09:42) | runner logs |
| Fees paid by the box runners | **361,814 tKAS** | runner `fee_tkas` |
| Best 1 min, box only | **4,253 tx/s** (Fri 01:24:46) | `data/legs_box.csv` |
| Best 10 min, box only | 3,717 tx/s (Fri 01:16:11) | same |
| Best 60 min, box only | 2,518 tx/s (Fri 21:57, leg 4) | same |
| Best 10 s, box only (bursty, indicative) | 4,700 tx/s (Fri 09:52:59) | same |
| Time at ≥100 tx/s | 11.5 h, spread over 20.5 h of legs | same |
| Does the data show "~5k TPS"? | **Not as unique included transactions.** See [below](#the-5k-tps-question) | |
| stp's block share | 50–63% while the box miners ran; 25% over the whole first night | `data/block_share_*.csv` |
| Public API under load | Lagged up to 11.7 min on Thursday, and **froze for about 85 min** on Friday night (HTTP 503). **Every episode we saw end was back to normal within 2–5 min of its last bad sample** (two ended inside sampler gaps), much better than the 25 Sep test, when the same API's indexer stayed frozen for at least 3 days 15 hours ([below](#api-recovery-vs-earlier-tests)) | `data/api_*.csv` |
| Mainnet cost of the whole test, same txs at 100 sompi/g | **45,464 KAS** (USD 1,929). At 150 sompi/g: 68,195 KAS (USD 2,894) | `data/mainnet_actual_test.csv` |

## What we're sure of / what we're not sure of

**Sure (measured, with source):**

| Fact | Source |
|---|---|
| 58,905,910 box txs included on n0's virtual chain in 4 legs, 152 rejected, 361,814 tKAS fees | runner `rep`/`final` lines, `data/legs_box.csv` |
| Box peaks: 4,253 tx/s best 1 min (Fri 01:24:46), 3,717 best 10 min, 2,518 best 60 min (L4, from 21:57) | `data/legs_box.csv` (1-s interpolation, [methodology](methodology.md#3-throughput-method-runners_tpspy)) |
| Leg 4 ran: Fri 21:52 → Sat 01:06, 14,018,548 included | runner logs, `run/timeline.md` |
| stp's block share 50–63% while the box miners ran (L1 P2W 60.3%, L2 62.8%, L3 58.1%, L4 52.6%), 25.1% over the first night, 29.7% before the storm | `data/block_share_legs.csv`, `data/block_share_sampler2.csv` |
| Public API: lag up to 704 s on Thursday; full freeze ≈22:02–23:28 on Friday (HTTP 503 every sample 22:09–23:27); every episode observed to its end was back to normal 2–5 min after its last bad sample | `data/api_events.csv`, `data/api_windows_vs_load.csv` |
| Earlier test (25 Sep): the same API's indexer froze at 21:55:38 CEST and was still frozen (HTTP 503) on 29 Sep 12:56 CEST | STP-KAS/tn10-indexer-stall-2026-09 `README.md` l.7–9, l.33–36 ([below](#api-recovery-vs-earlier-tests)) |
| Mainnet parameters: 10 BPS, 500,000 g block mass, minimum relay fee 100 sompi/g; live normal estimate 100 sompi/g on 3 Oct | rusty-kaspa `01b532e`, PR #1004, `data/sources/api.kaspa.org-info-fee-estimate.json` |
| Mainnet plain cost of the whole test: 45,464 KAS at 100 sompi/g, 68,195 KAS at 150 | `data/mainnet_actual_test.csv` |

**Not sure (estimates, inferences, unverified or quoted):**

| Item | Why it is not verified |
|---|---|
| Desk numbers to Fri 09:40 (16.97M submits, 15.70M acks, 1.27M rejects) | **Quoted** from Grok Build's own read of its desk log. The copy we have ends Thu 23:23; an ack is not inclusion |
| ~57% of fees came back to stp (204,740 tKAS; net ≈157k tKAS) | **Estimate**: fees × block share per window. Coinbase outputs were not summed |
| qp4jge's API view froze | **UNVERIFIED**: one slow call, the response was not saved |
| qp4jge 10.66M txs | **Attributed**: value from a logged API call, raw response not saved |
| TN10 stream/explorer view froze for days in the earlier test | **stp's report.** No file found for the stream/explorer; what is documented is the REST API freeze above. Neither test monitored the stream/explorer |
| The ">5k TPS" figure | Only the n0 "Processed" counter (double-counts parallel blocks, all senders) and single 10-s steps go above 5k. Not reached as unique box inclusion |
| L4 network-wide unique count | The indexer was frozen for much of L4, so its hourly counts under-count |
| Duration-table rows beyond 1 h | **Extrapolation**: no rate was held longer than ~1 h |
| Third-party covenant txs stuck pending in the mempool during the peak | stp observed that third-party covenant transactions on TN10 got **stuck pending in the mempool** during the peak (observed by stp, not measured by our tooling). We logged only n0's mempool *size*, which was large and evicting (§4b), not its composition |
| Covenant tx/hour at least halved during the peak | stp observed covenant tx/hour roughly halving during the peak (not measured by our tooling). The public tx counts we saved split only regular vs coinbase |
| Why the API froze and how it recovered | No indexer-side logs. The 4,020 s → 8 s jump in 2 min (Fri 23:27→23:29) looks like a restart or skip, not a catch-up (**inference**) |

## What

stp's box node **n0** (rusty-kaspa kaspad 2.1.0, TN10, one 8-core Xeon VM with 15 GB RAM and a 126 GB disk) was loaded by our own index-free runners in four legs. Grok Build sent extra load from stp's desk PC through public TN10 nodes, using the wallet `kaspatest:qp4jge54…`.

- **Runners.** At first these were "SMX": signed 1-in-1-out P2PK hops of about 1,752 g. From Thu 21:42 they were "P2W": unsigned 1-in-1-out hops between pay-to-script-hash lane addresses whose redeem script is `push4(id) OP_DROP OP_TRUE`, about 643 g each (`storm-p2w-runner.mjs`). P2W outputs are **anyone-can-spend**. That was fine for throwaway testnet coins. It matters for the mainnet section.
- **Funding.** The runners were funded from the coinbase outputs of stp's TN10 mining address `kaspatest:qzffl5…`.
- **Fees.** The feerate was a multiple of n0's own fee estimate. It was 3× and floating until the pause at Fri 00:10. After the restart it was a fixed 6,000 sompi/g (30×) from 01:09:50 to 01:26:51, when the fee-float guard cut it to 3×. From 01:33:41 it was a flat 2× capped at 400 sompi/g (`feerate.jsonl`, `run/timeline.md`).

## Why

There were three goals:

- Find the ceiling of one box plus stp's hashrate on TN10.
- See whether the public API's view of mined blocks (`api-tn10.kaspa.org`) breaks during a storm. The explorer pages and live block stream were not monitored.
- Learn what such a storm costs in fees.

## When

| Leg | Window (CEST) | What happened | Box included | Fees (tKAS) |
|---|---|---|---:|---:|
| **L1** | Thu 1 Oct 20:35:18 → Fri 07:52:54 | SMX ramp, then P2W. RAM STOP 23:13, planned pause 00:10–01:10 for an n0 rebuild, **30× fee 01:10–01:27**, box miners halted 01:31:50, then ~300 tx/s all night. RAM STOP 07:52:54 | 29,884,172 | 291,967 |
| **L2** | Fri 09:07:39 → 10:15 | 6 P2W runners, flat 2× fee. 09:43: 4 RPC connections per runner lifted rate from ~2,260 to ~2,900 tx/s. Disk pause at 19.5 GB from ~09:55. Box rebooted 10:15 | 6,815,084 | 14,811 |
| **L3** | Fri 11:49:49 → 16:50:47 | Knee test: 6 runners 2,410 tx/s, 7 runners 2,383 (flat), 8 runners **collapsed to 1,165** (12:11, blocks mass-full at 492k, mempool 14k→79k). Disk pause from 13:03:41. Disk STOP 16:50:47 | 8,188,106 | 20,239 |
| **L4** | Fri 21:52:07 → Sat 01:06:29 | n0 running without the utxoindex (restarted 17:26; no utxoindex line in the kaspad log). 6 runners, flat 2×. Best 5 min 3,258 tx/s (23:15). RAM/sink-age back-offs 23:30 and 23:44, then ~0. Hard abort on sink age 10.1 s at 00:29:55. Disk STOP 01:06:29 | 14,018,548 | 34,797 |
| **All** | | | **58,905,910** | **361,814** |

Sources: `run/timeline.md`, runner `rep`/`final` lines, `data/legs_box.csv`. n0 was wiped and resynced on Sat 3 Oct, so a live node query will not show this history. Only the logs do.

## Facts

### 1. Throughput, box only (unique transactions our runners saw accepted on n0's virtual chain)

| Leg | Best 10 s* | Best 1 min | Best 5 min | Best 10 min | Best 60 min | Median 5-min bin while loaded | Avg while ≥100 tx/s | Hours ≥100 tx/s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| L1 | 4,478 (01:25:27) | **4,253** (01:24:46) | **3,843** (01:21:15) | **3,717** (01:16:11) | 1,977 (Thu 22:12) | 327 | 1,033 | 8.04 |
| L2 | **4,700** (09:52:59) | 3,371 (09:54:03) | 2,913 (09:44:22) | 2,855 (09:39:01) | 1,893 | 2,161 | 2,333 | 0.81 |
| L3 | 3,263 (12:00:03) | 2,789 (11:55:30) | 2,478 (11:55:34) | 2,359 (11:55:27) | 1,950 | 1,990 | 1,977 | 1.15 |
| L4 | 4,054 (23:19:17) | 3,617 (23:18:42) | 3,258 (23:15:15) | 3,115 (23:13:38) | **2,518** (21:57) | 2,499 | 2,530 | 1.54 |

\*Runners report every 10 s, so 10-s values are the step between two reports. They depend on when blocks happen to be accepted, so they are indicative only. A 10-s grid without interpolation gives 4,537 for L1, the figure in the earlier private analysis. The 1-min and 5-min L1 values match that analysis (4,248–4,256 and 3,841–3,850) within the interpolation method.

- **L1's median is low (327)** because after the box miners stopped at 01:31:50 inclusion fell to ~300 tx/s for five hours, while blocks were only 11–26% full by compute mass (kaspad log, private box report). Before that, with miners on, the 5-min median was 1,757 (`run/final-numbers-2026-10-02.md`).
- **Ceilings, in the order they were hit:**
  - First, block compute mass. 1,752 g SMX hops fill a 500,000 g block at ~285 txs.
  - Then per-process submit throughput: about 700–850 tx/s per P2W process on Thursday (timeline 22:25–22:31), and about 380 per runner over one wRPC connection on Friday in L2 (about 480 with 4 connections).
  - Then block mass again once P2W ran at 6–8 runners. In L3, 8 runners pushed blocks to 492k and throughput collapsed.
  - Then disk: each leg ended on a disk pause or a disk STOP.

### 2. Network-wide view (everything n0 saw, including Grok Build's desk load and other TN10 senders)

These are different meters. Do not add them to the box numbers.

| Leg | n0 "processed" tx/s, best 1 min | best 10 min | best 60 min | Mean compute mass/block when loaded |
|---|---:|---:|---:|---:|
| L1 | 7,409 (01:24:46) | 6,488 | 4,541 | 354,922 g (71%) |
| L2 | 6,375 | 5,357 | 3,675 | 337,303 g (67.5%) |
| L3 | 6,269 | 5,470 | 4,895 | 369,684 g (73.9%) |
| L4 | **8,965** (22:50:31) | 8,218 | 6,849 | 396,651 g (79.3%) |

Source: n0 kaspad log, `Processed N blocks … (M transactions …)` every 10 s, minus one coinbase per block (`data/network_view.py`, `data/network_legs.csv`). **"Processed" counts a transaction once for every block body that carries it.** In a DAG with 2–3 blocks merged per step the same transaction often sits in several parallel blocks. So this is an upper bound, not unique throughput. At the L1 peak minute, n0 processed 7,409/s while the box saw 4,253/s of its own txs accepted, and a block sample at 01:17 showed 97% of block mass was ours (timeline). The ratio was about 1.7 processed per unique accepted tx *(inference)*.

**Unique network-wide throughput** is only available per hour, from the public indexer (`GET api-tn10.kaspa.org/transactions/count/<day>`, fetched Sat 15:55 UTC; `data/hourly_network_vs_box.csv`):

- Best hour: Thu 22:00–23:00, **9,833,770 regular txs = 2,732 tx/s**. The box share was 1,875 tx/s and other senders 857 tx/s.
- Fri 09:00 hour 2,141 tx/s (box 1,878). Fri 12:00 hour 2,341 tx/s (box 1,889).
- **L4 hours do not reconcile.** For Fri 22:00–23:00 the indexer reports 3.95M while our runners saw 8.68M of their own txs accepted in the same hour. The indexer was frozen for most of that hour (see §4). Its hourly count for that window is **incomplete or shifted. Cause UNVERIFIED.**

**Grok Build's desk sender** (stp's desk PC → public TN10 nodes; wallet qp4jge):

- Grok Build's own read of its full desk log (`analysis/desk-public-read-2026-10-02.md` in the private analysis repo) covers Thu 20:38 to Fri 09:40. It reports 16,972,123 submits, 15,697,431 node acks and 1,274,692 rejects (7.5%). An ack means a node accepted `submitTransaction`. It does not mean the tx was included.
- The part of that log in the repo, to Thu 23:23, sums to 8,276,238 / 7,686,305 / 589,933 (`data/desk_sender_summary.csv`).
- The public API reported 10,659,746 txs for qp4jge at Fri 07:55. That value is recorded in notes, not as a raw response, so it is **attributed, not re-verified**.
- The desk's own numbers for the Friday-evening run (L4) are **not on the box**. See "Missing" below.

### 3. Fees, block share, and why the TN10 cost was lower than the gross fee

- **Fees paid by the box runners: 361,814 tKAS** for 58.9M txs. That is 0.00614 tKAS per tx on average, at a mean feerate of 796 sompi/g. By leg: L1 291,967 (mean 1,090 sompi/g; 122,320 of it in the 24 minutes at 30×), L2 14,811 (337), L3 20,239 (384), L4 34,797 (386).
- Not in that total: the transfers to Grok Build's wallet (836.9 + 11,647.7 tKAS fees on Thu/Fri), TN10 ops' 3.0M tKAS send to Build on Fri 09:01–09:08 (35,020.6 tKAS fees, timeline 10:39), sweeps (~16 tKAS), and KNS (§6).

**Who mined the blocks n0 saw** (`data/block_share_legs.csv` from `host.jsonl`, and the independent 5-minute sampler `data/block_share_sampler2.csv`):

| Window | stp total (box + desk) | Box | Desk | Rest of TN10 |
|---|---:|---:|---:|---:|
| Before the storm, Thu 18:41–20:35 | 29.7% | 0% | 29.7% | 70.3% |
| L1 SMX, Thu 20:35–21:42 | 57.2% | 34.9% | 22.3% | 42.8% |
| L1 P2W with box miners on, 21:42–01:32 | **60.3%** | 59.7% | 0.5% | 39.7% |
| L1 box miners off, 01:32–07:53 | **0.6%** | 0% | 0.6% | 99.4% |
| **L1 whole night** | **25.1%** | 21.8% | 3.3% | 74.9% |
| L2 | **62.8%** | 62.8% | 0% | 37.2% |
| L3 | 58.1% | 56.3% | 1.8% | 41.9% |
| L4 (independent sampler only; the host sampler's counter read 0 after n0's restart) | **52.6%** | 53.3%† | n/a | ~47% |

†Box miners' accepted submits divided by DAA growth. The "all blocks through n0" column gives 52.6%. Where the two samplers cover the same window (L1 whole, L2, L3), they agree within about 1 point: 25.1 vs 26.2%, 62.8 vs 62.1%, 58.1 vs 57.6%.

**The 60–70% claim.** stp's own blocks were 50–63% of TN10 blocks in the windows where his box miners were running. They were **never 70%**. Over the whole first night they were 25%, because the box miners were off after 01:32 and desk blocks through n0 almost stopped after Thu 21:28. **So "60–70%" is not supported. "About 50–63% while the box miners ran, 25% across leg 1" is.**

**Fee recapture on TN10 (inference).** A miner collects the fees of the transactions in the blocks it mines. Multiplying each window's fees by stp's block share gives about **204,740 tKAS back to stp's address, 56.6% of the fees, and a net TN10 fee cost of about 157,074 tKAS** (`data/fee_recapture_estimate.csv`). The fee-weighted share (56.6%) is far above the night-long block share (25%) because most fees were paid while the box miners ran. This estimate assumes our txs were spread over all miners' blocks in proportion to block share. The logs suggest our txs actually sat mostly in our own blocks: inclusion collapsed when the box miners stopped even though blocks were mostly empty. If so, the real recapture was higher. Per-block fee attribution was not logged, so this is **UNVERIFIED**. **None of this applies to mainnet** (below).

### 4. Public API (api-tn10.kaspa.org)

Probes:

- `GET /info/health` every 120 s: indexer lag `acceptedTxBlockTimeDiff`, DB sync flag, HTTP status.
- Every 300 s: the newest coinbase of stp's mining address on `/addresses/<qzffl5>/full-transactions-page`, compared with the blocks n0 saw us mine.

`stall_suspected` = indexer more than 120 s behind while the API's kaspad backends were synced, so the API database is behind the chain, not the node. Source: `data/api_legs.csv`, `data/api_events.csv`, `data/api_gaps.csv`.

| Window | Health samples | HTTP 503 | Timeouts | Stall samples (first–last) | Max indexer lag | Mined-view samples | Max newest-coinbase lag | `mined_stall` |
|---|---:|---:|---:|---|---:|---:|---:|---:|
| Thu baseline 18:41–20:35 | 57 | 0 | 1 | 0 | 5 s | 22 | 11 s | 0 |
| L1 | 315 | **28** | 20 | 48 (Thu 22:29 – Fri 01:30) | **704 s** (Thu 23:19) | 43 | **652 s** (Thu 23:16) | 9 |
| L2 | 34 | 0 | 8 | 2 (09:55–09:57) | 166 s | 0 (watcher down) | – | – |
| L3 | 151 | 2 | 7 | 4 (12:33–12:47) | 170 s | 56 | 302 s | 3 |
| **L4** | 97 | **40** | 1 | 41 (22:05 – 23:27) | **4,311 s** (23:21) | 39 | **4,138 s** (23:18) | 0‡ |

- **Thursday (L1): lag, not a freeze.** The indexer fell up to 11.7 min behind. The mined-coinbase view lagged up to 10.9 min. 28 HTTP 503s, 22 of them with the DB reporting `isSynced:false`. Each episode cleared within minutes (timeline below).
- **Friday night (L4): a full freeze, about 85 minutes from first lag to recovery (≈22:02–23:28).** The indexer lag started building at 22:01. From about 22:10 the indexer's accepted-tx pointer stopped completely: from 22:23 to 23:21 the lag grew by exactly 120 s per 120-s sample. Every health call from 22:09 to 23:27 returned **HTTP 503** with `isSynced:false`. The newest coinbase shown for stp's mining address froze at the same time. Its lag grew from 89 s (22:03:55) to 4,138 s (23:18:55), the same coinbase id was shown from 22:23 to 23:18, and the lag was back to 9 s at 23:28:55. Meanwhile n0 kept seeing stp's miners win ~50% of blocks (independent sampler), so the address view was stale, not quiet. ‡The sampler's own `mined_stall` flag missed this, because its "blocks we mined" input came from the host sampler's share counter, which read 0 after n0's Friday restart.
- **Address-level freezes.** The only address read on a schedule was stp's mining address (qzffl5). Its page timed out (20 s) 22 times across all windows, plus the L4 freeze above. Grok Build's wallet qp4jge was read 13 times on Fri 07:52–07:57. One `transactions-count` call needed a retry with a 60-s timeout. The first attempt's result was not saved, so **"qp4jge's view froze" is UNVERIFIED**. No other addresses were probed.
- **Measurement gaps:** mined-view watcher **Fri 00:06–08:45** (it crashed on restart at 01:00:31, so the 01:24 peak has no mined-view data) and 08:45–12:13. Health probe Fri 00:09–01:00, 08:44–09:07 and 10:13–11:49.
- n0 itself stayed synced throughout L1 (4,297 of 4,297 RPC polls; sink age max 3.1 s, private box report). In L4 a hard abort fired on a 10.1-s sink age (00:29:55).

#### API recovery vs earlier tests

**This time the public API recovered within hours (measured); in the earlier test it stayed frozen for days (source below). So recovery looked much better this time, though the two tests did not use exactly the same measurements.** In this run the longest episode lasted 86 minutes. Every episode we could watch to its end was back to normal (HTTP 200, lag <120 s) within 2–5 minutes of its last bad sample. Two Thursday-night episodes ended inside sampler gaps. The health probe was back to normal by 01:00 at the latest.

**What we measured, and what we didn't.** This run's numbers come from the **REST API** (`api-tn10.kaspa.org`: `/info/health` every 120 s, and the qzffl5 address page every 300 s). We **did not monitor the TN10 stream/explorer view** (live block stream, websocket, explorer pages). So none of this says how the explorer behaved.

**(1) Each episode against the load at the time** (`data/api_windows_vs_load.csv`, script `data/api_vs_load.py`). Box = our included tx/s from 5-min bins. n0 processed = all senders, counting a tx twice if it sits in two blocks (upper bound). "Recovered" = first sample with HTTP 200 and lag <120 s.

| Episode (CEST) | Length | Box tx/s in window (hour before) | Best box 5-min bin in window | n0 processed tx/s | Recovered | Peak lag |
|---|---:|---:|---|---:|---|---:|
| Thu 22:29–23:31 health stall, intermittent 503 | 62 min | 1,477 (1,730) | 2,752 (22:40) | 3,591 | 23:33 (+2 min) | 704 s |
| … inside it: Thu 23:03–23:29 continuous 503 | 26 min | 951 (1,920) | 2,231 (23:00) | 2,705 | 23:33 (+4 min) | 704 s |
| Thu 22:56–23:31 coinbase view `mined_stall` | 35 min | 1,141 (1,875) | 2,231 (23:00) | 3,047 | 23:36 (+5 min) | 652 s |
| Thu 23:53–Fri 00:09 health stall + 503 | 16 min | 2,421 (1,531) | 2,850 (23:50) | 4,217 | by 01:00 (sampler down 00:09–01:00) | 527 s |
| Fri 00:01–00:06 coinbase view `mined_stall` | 5 min | 2,284 (1,567) | 2,340 (00:05) | 3,918 | not observed (watcher down 00:06–08:45) | 431 s |
| Fri 01:22–01:30 503 with 18-s responses, then stall | 8 min | 2,161 (728) | 3,677 (01:20) | 5,427 | 01:32 (+2 min); lag ≤6 s from 01:38 | 163 s |
| Fri 09:55–09:57 health stall (6 timeouts 09:39–09:51 before it) | 2 min | 1,645 (1,878) | 1,645 (09:55) | 4,948 | 09:59 (+2 min) | 166 s |
| Fri 12:25–12:47 two 503s + intermittent stall | 22 min | 2,005 (1,203) | 2,137 (12:35) | 5,340 | 12:49 (+2 min) | 170 s |
| **Fri ≈22:02–23:28 full freeze** (503 on every sample 22:09–23:27) | **86 min** | 2,435 (336) | 3,238 (23:15) | 6,546 | **23:29 (+2 min)** | **4,311 s** |
| Fri 22:03–23:23 coinbase view frozen | 80 min | 2,454 (336) | 3,238 (23:15) | 6,587 | 23:28 (+5 min) | 4,138 s |

How this lines up with load:

- **Every stall episode (indexer or coinbase view more than 120 s behind) happened while load was high.** Averaged over each episode, box load was about 950–2,450 tx/s and n0 processed was 2,700–6,600 tx/s. There were no stalls in the pre-storm baseline, none during the L1 night at ~300 tx/s, and none on Saturday after the storm (0 stall samples in 505, max lag 14 s).
- Single HTTP 503s with the indexer up to date (lag ≤8 s) also happened outside load, e.g. Fri 07:46 and Sat 03:59, along with 502s on Saturday. These are not stalls.
- **It does not line up exactly with the peaks:**
  - The first Thursday stall sample (22:29:30) came as an **outside** burst from about 22:29:20 filled blocks by storage mass. Our own inclusion dropped during that burst: 339 tx/s in the 22:30 5-min bin (`data/box_5min.csv`) and ~196 tx/s for 22:32–22:36 (timeline l.29–30). So other senders' load counted, not just ours.
  - The longest Thursday 503 run (23:03–23:29) came while our load was *falling*: the RAM STOP was at 23:13, and box load averaged 951 tx/s against 1,920 the hour before. It trailed the busiest hour rather than matching it. The busiest unique hour network-wide was Thu 22:00 (2,732/s on the indexer).
  - The single highest box minute (Fri 01:24:46, during the 30× fee burst) produced only an 8-minute blip with lag ≤163 s.
  - The Friday freeze did not follow one peak. It started about 5 min after L4 load came on (21:57) and lasted almost the whole loaded phase. The L4 peak (23:15) fell inside it. It ended at 23:29, as our load was tapering (2,125 → 1,537 tx/s) and about 10 min before our runners stopped.
- Timeouts (20 s) on `/info/health` happened at all hours, including Saturday with no load from us (38 of 505 samples). They are not counted as stalls.
- The 5.4-h "coinbase lag" on Saturday morning is not a freeze. n0 saw stp mine 0 blocks then (`node_ours_last_window` = 0), so there was no newer coinbase to show.

**(2) The earlier test.** Source: stp's private note **STP-KAS/tn10-indexer-stall-2026-09, `README.md` (commit `22780de`, 29 Sep 2026)**:

- l.7–9: "`api-tn10.kaspa.org` … accepted-transaction processing has not moved since 2026-09-25 19:55:38Z (21:55:38 CEST). `/info/health` returns HTTP 503 with `database.isSynced:false`."
- l.30: "Checked again: still frozen, 503 | 29 Sep 10:56Z | 12:56".
- l.33–36: `acceptedTxBlockTimeDiff` 313,243.74 s ("about 3 d 15 h") on 29 Sep 10:56:22Z. The same note's `evidence/api-health-2026-09-29.txt` l.3 has the `HTTP/2 503`.
- l.12–14: whether that storm caused it is "Unproven … Time correlation is not causation."

The end of that freeze was not recorded. The earliest healthy sample we have is **1 Oct 18:27:39 CEST**, from the dry run of this test's sampler (lag 3 s, box file `artifacts/stress-tests/dryrun/api-health-min-dry.jsonl`, line 2). So the earlier freeze lasted **at least 3 days 15 hours and at most about 5 days 21 hours**.

**How comparable the two are.**

- For the REST API this is closer to like-for-like than expected. Both tests read the same field (`acceptedTxBlockTimeDiff`, HTTP 503 with `isSynced:false`) on the same endpoint.
- The sampling differed. The earlier test had spot checks days apart; this one sampled every 120 s.
- The load counters differed too. The earlier note quotes n0's `u-tps` counter at ~6,000 at the freeze; this report uses "Processed" and per-runner inclusion.
- stp also remembers the **TN10 stream/explorer view** staying frozen for days in an earlier test. No file we found documents that view, and **neither test monitored it** (stp's report; API involvement for that view unverified).
- Why the API recovered quickly this time is unknown. It could be operator action, indexer changes since 25 Sep, or the load pattern; we have no indexer logs.

### 4b. Mempool and third-party transactions (context only)

stp saw third-party covenant transactions on TN10 **stuck pending in the mempool** during the peak, and covenant tx/hour on TN10 at least halving. **Our tooling did not measure either.**

- We logged n0's mempool **size** and fee estimate, not its **composition**: no txids, script types or pending times.
- The public `transactions/count` data we saved splits only `regular` vs `coinbase`, with no covenant or script-type breakdown.
- No covenant or vprogs stats were sampled.
- We made no new queries to n0 for this.

What the logs do show is that n0's mempool was crowded and fee-competitive at those times. That is consistent with stp's observation but does not prove it (`data/mempool_windows.csv`, `data/mempool_evictions_10min.csv`, script `data/mempool_view.py`):

| Window (CEST) | n0 mempool median / max (txs) | n0 fee estimate "normal", median (max) sompi/g | Evicted for higher feerate |
|---|---:|---:|---:|
| Pre-storm baseline | 0 / 216 | 100 (100) | 0 |
| L1, box miners on (20:35–01:32) | 3,038 / 99,803 | 195.7 (6,415) | 59,081 (01:06:36–01:07:36, while the feeder refilled lanes just before the 30× restart) |
| L1 peak incl. 30× fee burst (01:10–01:30) | 64,992 / 77,480 | 1,541 (2,328) | 0 |
| L1 night, box miners off (01:32–07:53) | 71,498 / 99,992 | 193.9 (24,145) | **427,059** (01:33–02:12) |
| L4 loaded (21:57–23:38) | 17,140 / 30,826 | 194.2 (212) | 0 |
| After the storm (Sat 01:06–17:00) | 0 / 13,757 | 100 (730) | 0 |

- During the loaded legs, n0's "normal" estimate sat at about 2× the 100 sompi/g floor. During the 30× burst it went far higher. A third-party tx paying the floor would have queued behind tens of thousands of higher-feerate storm txs *(inference)*.
- In total n0 evicted **486,140** txs "in favor of incoming higher feerate transactions" on Fri 01:06–02:12 (kaspad log). Most of that came *after* the box miners stopped, not at the throughput peak. We can't tell whose txs were evicted; most were probably ours *(inference)*.

### 5. Limits of this test (honest list)

- **One box.** 8 vCPU, 15 GB RAM, 126 GB disk, shared by n0, the box miners (nice 19), the runners and the samplers. The load average reached ~28–32 on 8 cores in L2 (timeline 09:19, 09:31).
- **Caps:**
  - Block compute mass: SMX filled blocks at ~285 txs. P2W at 6–8 runners pushed blocks to 492–499k g; in L3, adding the 8th runner made throughput fall.
  - Submit throughput per process: ~700–850 tx/s per P2W process on Thursday, ~380 per runner over one wRPC connection on Friday (L2), ~480 with 4 connections.
- **RAM:**
  - Two storm-watch STOPs at RAM below 1 GB: Thu 23:13:34 (1,009 MB; a read-only scan script contributed) and Fri 07:52:54 (754 MB; most likely a large outside read-only probe for qp4jge, timeline 08:08 *(inference)*).
  - The coinbase feeder had to be restarted on RSS more than 10 times.
  - **n0 was OOM-killed at Fri 00:50** by one `getUtxosByAddresses` call on stp's mining address, which holds a huge number of coinbase UTXOs (kernel: kaspad anon-rss 9.46 GB).
- **Disk.** 4.5–7 GB/h at load. Every leg ended on disk: L1 at the 25 GB self-pause, L2 at 19.5 GB, L3 and L4 at the 21 GB pause and then a STOP after 15 min under 19 GB. The Fri 08:09 pruning low point was 9.15 GB.
- **Fee float feedback loop.** "3× the node's normal estimate" chased its own backlog: up to 19,244 sompi/g (Thu 23:56). The 30× runner segment (01:09:58–01:33:41; 6,000 sompi/g until 01:26:51, then 3×) cost 122,320 tKAS, 42% of L1 fees, for 11.5% of L1's included txs (private box report). A flat 2× then lost to outside senders while n0's normal estimate hit 24,145 (Fri 01:51).
- **Pruning windows.** TN10 pruning-point moves happen about every 12 h. The kaspad log shows them Thu 19:36–20:13, Fri 07:53–08:30 and Fri 19:37–20:22, and they eat disk and RAM. The Friday-evening leg was held outside an 18:55–20:15 pruning window (`run/GO-next-leg.md`).
- **Own hashrate decided inclusion.** After the box miners stopped (Fri 01:31:50), our inclusion fell to ~300 tx/s with blocks mostly empty *(inference: other TN10 miners included few of our txs)*.

### 6. KNS during the storm (separate bot)

- **Thu 1 Oct:** 18,524 names in three runs (9,509 + 8,258 + 757), 0 failures. **Ownership was verified for all 18,524** against `api.knsdomains.org/tn10` on Fri 12:10–12:16, with 0 API errors (`artifacts/kns-tn10/*-2026-10-01/ownership-verification*.json`).
- **Fri 2 Oct:** 58 names (09:34) plus 11,400 names (11:49–12:53, during L3), 0 failures, 714.6 tKAS fees (`funded-2026-10-02/final-summary.json`). Ownership of the Friday names was not verified here.

## The "~5k TPS" question

stp said it "sometimes reached ~5k TPS". What the data shows:

- **Unique box transactions included: no.** The best was 4,253/s over a minute and 3,717/s over 10 minutes. Short 10-s steps reached 4,478 (L1) and 4,700 (L2). Those are measurement-granularity bursts, not a rate.
- **Unique network-wide: only hourly data exists.** The best hour was 2,732/s.
- **n0's "processed" counter: yes, well above 5k.** 7,409/s for a minute in L1, and 8,965/s for a minute and 8,218/s for 10 minutes in L4. But that counter counts a tx once per block that carries it, plus everyone else's traffic. A block-explorer TPS gauge that counts txs in blocks would show figures like this. **That this is where the 5k came from is UNVERIFIED.**
- **L4, all senders together.** In L4 other senders (probably Grok Build's desk; not verified) were heavy, and processed was 3.3× our box rate. Unique network-wide TPS for L4 at minute resolution **cannot be measured from these logs**: the indexer was frozen.

**Plain answer:** the box alone peaked at about **4.25k tx/s for a minute**. "5k" is only reached by meters that double-count, or in 10-second bursts close to it.

## What this means for mainnet

**Headline: the plain storm cost.** Same tx count and same measured mass, priced at **(a) the mainnet normal feerate, 100 sompi/gram** and **(b) priority, 1.5× = 150 sompi/gram**.

- **No fee recapture.** A mainnet sender without hashrate gets nothing back.
- **No fee-market or bidding-war escalation model.** This was left out on purpose. stp's call: sustaining this much compute on mainnet is not realistic anyway, so the floor price is the meaningful number.

**Mainnet parameters used** (checked Sat 3 Oct 2026, 15:54–15:59 UTC):

- **Block rate 10 per second.** `blockrate: BlockrateParams::new::<10>()` in `MAINNET_PARAMS`, rusty-kaspa master [`consensus/core/src/config/params.rs`](https://github.com/kaspanet/rusty-kaspa/blob/01b532e8b553523216471682649693af92f0fd16/consensus/core/src/config/params.rs) (commit 01b532e, latest release v2.1.0 of 22 Sep 2026). Cross-check: mainnet virtual DAA score on `api.kaspa.org/info/blockdag` rose 2,617 in 272 s (≈9.6/s).
- **Block mass limits:** compute 500,000, storage 500,000, transient 1,000,000 (same file). Transient mass is normalized ×0.5 to the compute scale ([`consensus/core/src/mass/mod.rs`](https://github.com/kaspanet/rusty-kaspa/blob/01b532e8b553523216471682649693af92f0fd16/consensus/core/src/mass/mod.rs)). For these tx shapes compute mass binds. A P2W hop is ~273 bytes: 546 normalized transient g against 643 compute g. **Capacity = 10 × 500,000 = 5,000,000 g/s.**
- **Minimum relay fee: 100 sompi/gram.** `DEFAULT_MINIMUM_RELAY_TRANSACTION_FEE = 100_000` sompi per kg ([`mining/src/mempool/config.rs`](https://github.com/kaspanet/rusty-kaspa/blob/01b532e8b553523216471682649693af92f0fd16/mining/src/mempool/config.rs)), raised from the old 1 sompi/g by [rusty-kaspa PR #1004](https://github.com/kaspanet/rusty-kaspa/pull/1004) (merged 15 May 2026). **The "standard 1 sompi/gram" no longer applies.** The live mainnet estimate agrees: `api.kaspa.org/info/fee-estimate` at 15:54:08 and 15:58:00 UTC returned priority, normal and low all at **100 sompi/g**. So (a) = 100 and (b) = 150.
- **Price:** Kraken public ticker, last trade **KAS/USD 0.04243** (15:57:59 UTC = 17:57:59 CEST) and **KAS/EUR 0.03778** (15:58:05 UTC). Cross-check: `api.kaspa.org/info/price` gave 0.04247025 at 15:57:59 UTC. CoinGecko returned HTTP 429 (rate limit) at 15:54 and 15:58 UTC and was not used.

### A. The actual test, repriced for mainnet (`data/mainnet_actual_test.csv`)

| Leg | Txs | Avg mass | KAS @ 100 | KAS @ 150 | USD @ 100 / 150 | At the feerates we actually used |
|---|---:|---:|---:|---:|---:|---:|
| L1 | 29,884,172 | 895.9 g | 26,773 | 40,160 | 1,136 / 1,704 | 291,967 KAS (USD 12,388) |
| L2 | 6,815,084 | 644.3 g | 4,391 | 6,586 | 186 / 279 | 14,811 (628) |
| L3 | 8,188,106 | 644.3 g | 5,276 | 7,913 | 224 / 336 | 20,239 (859) |
| L4 | 14,018,548 | 643.8 g | 9,025 | 13,538 | 383 / 574 | 34,797 (1,476) |
| **All** | **58,905,910** | 771.8 g | **45,464** | **68,195** | **1,929 / 2,894** | 361,814 (15,352) |

The right-hand column is the side note: TN10 sompi = mainnet sompi, so the fees we paid are the KAS we would have paid on mainnet at the same feerates. On TN10 roughly 57% of that came back to stp's own mining address *(inference, §3)*, so the net TN10 cost was about 157k tKAS. **On mainnet nothing would come back**, and that is why this report uses the gross figures.

### B. Duration table, measured rates (`data/mainnet_scenarios.csv`, script `data/mainnet_scenarios.py`)

The shape is the P2W hop the peaks were measured with: 644.8 g including funding txs.

**peak 1 min (L1, Fri 01:24:46): 4,252.8 tx/s, P2W hop (measured avg incl. funding txs) 644.8 g** — mainnet capacity for this shape 7,754 tx/s; uses 54.8% of block mass; fits: yes

| Duration | Txs | KAS @ normal 100 sompi/g | KAS @ priority 150 sompi/g | USD normal | USD priority | EUR normal | EUR priority |
|---|---:|---:|---:|---:|---:|---:|---:|
| 30 min | 7,655,040 | 4,936 | 7,404 | 209 | 314 | 186 | 280 |
| 1 h | 15,310,080 | 9,872 | 14,808 | 419 | 628 | 373 | 559 |
| 2 h | 30,620,160 | 19,744 | 29,616 | 838 | 1,257 | 746 | 1,119 |
| 3 h | 45,930,240 | 29,616 | 44,424 | 1,257 | 1,885 | 1,119 | 1,678 |
| 4 h | 61,240,320 | 39,488 | 59,232 | 1,675 | 2,513 | 1,492 | 2,238 |
| 10 h | 153,100,800 | 98,719 | 148,079 | 4,189 | 6,283 | 3,730 | 5,594 |
| 12 h | 183,720,960 | 118,463 | 177,695 | 5,026 | 7,540 | 4,476 | 6,713 |
| 24 h | 367,441,920 | 236,927 | 355,390 | 10,053 | 15,079 | 8,951 | 13,427 |

**sustained: best 60 min (L4, Fri 21:57): 2,517.6 tx/s, P2W hop (measured avg incl. funding txs) 644.8 g** — mainnet capacity for this shape 7,754 tx/s; uses 32.5% of block mass; fits: yes

| Duration | Txs | KAS @ normal 100 sompi/g | KAS @ priority 150 sompi/g | USD normal | USD priority | EUR normal | EUR priority |
|---|---:|---:|---:|---:|---:|---:|---:|
| 30 min | 4,531,680 | 2,922 | 4,383 | 124 | 186 | 110 | 166 |
| 1 h | 9,063,360 | 5,844 | 8,766 | 248 | 372 | 221 | 331 |
| 2 h | 18,126,720 | 11,688 | 17,532 | 496 | 744 | 442 | 662 |
| 3 h | 27,190,080 | 17,532 | 26,298 | 744 | 1,116 | 662 | 994 |
| 4 h | 36,253,440 | 23,376 | 35,064 | 992 | 1,488 | 883 | 1,325 |
| 10 h | 90,633,600 | 58,441 | 87,661 | 2,480 | 3,719 | 2,208 | 3,312 |
| 12 h | 108,760,320 | 70,129 | 105,193 | 2,976 | 4,463 | 2,649 | 3,974 |
| 24 h | 217,520,640 | 140,257 | 210,386 | 5,951 | 8,927 | 5,299 | 7,948 |

*Side note, TN10 feerates actually used:* L1 1,090.5 sompi/g average, L2 337.3, L3 and L4 about 384–386 sompi/g (`data/legs_box.csv`, column `avg_feerate_sompi_per_g`). At ~385 sompi/g the duration rows above cost 3.85× the normal column. These were our choices on TN10, not mainnet requirements; the headline columns are (a) and (b).

All rate × shape combinations, 1 h and 24 h. The 30 min to 24 h rows for every combination are in the CSV.

| Shape | Rate | tx/s | Mainnet capacity for shape | Fits? | 1 h KAS normal / priority | 24 h KAS normal / priority | 24 h USD normal / priority |
|---|---|---:|---:|---|---:|---:|---:|
| P2W 644.8 g | peak 1 min (L1, Fri 01:24:46) | 4,252.8 | 7,754 | yes | 9,872 / 14,808 | 236,927 / 355,390 | 10,053 / 15,079 |
| P2W 644.8 g | peak 10 min (L1, Fri 01:16:11) | 3,717.3 | 7,754 | yes | 8,629 / 12,943 | 207,093 / 310,640 | 8,787 / 13,180 |
| P2W 644.8 g | sustained: best 60 min (L4, Fri 21:57) | 2,517.6 | 7,754 | yes | 5,844 / 8,766 | 140,257 / 210,386 | 5,951 / 8,927 |
| P2W 644.8 g | sustained: whole-test loaded average | 1,417.9 | 7,754 | yes | 3,291 / 4,937 | 78,992 / 118,488 | 3,352 / 5,027 |
| signed 1,751.9 g | peak 1 min (L1, Fri 01:24:46) | 4,252.8 | 2,854 | **no** (149.0% of capacity) | 26,822 / 40,233 | 643,722 / 965,582 | 27,313 / 40,970 |
| signed 1,751.9 g | peak 10 min (L1, Fri 01:16:11) | 3,717.3 | 2,854 | **no** (130.2% of capacity) | 23,444 / 35,167 | 562,666 / 843,999 | 23,874 / 35,811 |
| signed 1,751.9 g | sustained: best 60 min (L4, Fri 21:57) | 2,517.6 | 2,854 | yes | 15,878 / 23,817 | 381,074 / 571,612 | 16,169 / 24,253 |
| signed 1,751.9 g | sustained: whole-test loaded average | 1,417.9 | 2,854 | yes | 8,942 / 13,414 | 214,619 / 321,929 | 9,106 / 13,659 |

**Capacity.**

- Every measured rate fits on mainnet with the P2W shape. The 1-min peak uses 55% of mainnet block mass.
- With properly signed txs (~1,752 g), mainnet carries at most **2,854 tx/s**. The two peak rates (4,253 and 3,717) **would not fit**. Sustained 2,518 would fill 88% of every block.
- Today mainnet carries about 1 regular tx/s (desk public read, 2 Oct), so blocks are almost empty. With no fee-market model these costs assume the floor feerate gets included.

### Assumptions

1. **Tx shape and mass.** Mass is the TN10 measurement: P2W 644.8 g average incl. funding txs (runner `massH`/`massF`), SMX 1,751.9 g (from fee ÷ submitted ÷ feerate). Mainnet uses the same mass formula (`MAINNET_PARAMS`: 1 g/byte, 10 g/script-pubkey byte, 1,000 g/sigop).
2. **Anyone-can-spend lanes.** P2W lanes are anyone-can-spend. On mainnet anyone watching could take the coins sitting in the lanes. This report prices the fee only. An attacker who wants to avoid that would use signed txs: 2.7× the mass and cost, and capped at 2,854 tx/s.
3. **Policy.** Mainnet mempool policy accepts these shapes the same way TN10 kaspad 2.1.0 did. The minimum relay fee is charged on the larger of compute mass and normalized transient mass; storage mass is not charged ([`mining/src/mempool/check_transaction_standard.rs`](https://github.com/kaspanet/rusty-kaspa/blob/01b532e8b553523216471682649693af92f0fd16/mining/src/mempool/check_transaction_standard.rs) l.67–76).
4. **Price.** A flat price for the whole duration: Kraken last trade at 17:58 CEST Sat 3 Oct. A large buy of KAS to fund the fees would move it. Not modelled.
5. **Fees.** No fee recapture and no fee-market escalation (deliberate, see above). Coins in lanes are not spent, only fees. The lane float itself (tens of thousands of KAS on TN10) is capital, not cost.
6. **Rates.** "Peak" and "sustained" are box-only rates from one 8-core box. A better-provisioned sender could go higher, up to the capacity column.
7. **Duration rows** repeat the measured rate for the whole duration. **The test never held these rates that long:** the best full hour was 2,518 tx/s, and the longest unbroken run of 5-min bins at ≥2,000 tx/s was 55 min (Fri 22:00–22:55). Everything past 1 h is extrapolation.

## Claims vs verified

| Claim | What the data shows | Status |
|---|---|---|
| "Sometimes ~5k TPS" (stp) | Box unique: 4,253/s best minute; 10-s bursts 4,478–4,700. n0 processed (double-counting, all senders): 7,409–8,965/s best minute | ❌ as unique inclusion; ✅ only on the processed meter; source of the 5k **UNVERIFIED** |
| 10 s 4,537 / 1 min 4,248–4,256 / 5 min 3,850 (earlier analysis) | 10 s 4,478 interpolated (4,537 on a 10-s grid), 1 min 4,253, 5 min 3,843 | ✅ |
| stp mines 60–70% of TN10 | 50–63% while the box miners ran; L1 whole 25%; 0.6% after Fri 01:32 | ❌ as stated, ⚠️ close only while the box miners ran |
| Most fees came back to stp's address | Estimated 56.6% of fees, weighted by block share | ⚠️ estimate (inference) |
| Relaunch 09:12: ~6.82M included, peak 2,908 tx/s, disk pause 09:57 | 6,815,084 included; best 5 min 2,913 (09:44:22); disk pause ~09:55 | ✅ |
| Leg 3: knee 6 runners 2,410/s; 8 runners 1,165; mass 318k→492k; disk pause 13:03; STOP 16:50 | Timeline and runner logs agree; STOP_SET 16:50:47 | ✅ |
| Leg staged at 17:31 | **It ran**: Fri 21:52–Sat 01:06, 14.0M included, best 60 min 2,518/s | ✅ (new in this report) |
| API froze/lagged on some addresses | qzffl5 view lagged 10.9 min (Thu) and **froze ~85 min (Fri ≈22:02–23:28)**; qp4jge: one slow call, result not saved | ✅ for qzffl5; **UNVERIFIED** for qp4jge |
| API freeze only around the heaviest load, recovered fairly quickly (stp) | All stall episodes were under high load, including other senders' load, but not exactly at our peaks (see table). Each one observed to its end recovered 2–5 min after its last bad sample; the longest lasted 86 min | ✅ recovery; ⚠️ "at the peaks" only roughly |
| Earlier test: freeze lasted days (stp) | REST API indexer frozen ≥3 d 15 h from 25 Sep 21:55 CEST (tn10-indexer-stall-2026-09 README l.7–9, l.30, l.36). Stream/explorer freeze: no file | ✅ for the REST API; **UNVERIFIED** for the stream/explorer |
| KNS 18,524 names, ownership verified | 9,509 + 8,258 + 757 verified on api.knsdomains.org | ✅ |
| qp4jge 10.66M txs | Value from a logged API call; the raw response was not saved | ⚠️ attributed |

## Missing (needs files from stp's desk)

Grok Build's numbers for the Friday-evening run, and its desk log after Thu 23:23, are not on the box. To add the desk side of L4 and a full desk count, these files are needed (paths as written by the Build prompt):

- `C:\Users\Fermi\kaspa-tn10\build-storm2\final-report.json`: accepted, rejects, avg tx/s, spent, first/last txid
- `C:\Users\Fermi\kaspa-tn10\build-storm2\logs\` (status lines every 60 s)
- the full desk `sender.jsonl` behind `desk-public-read-2026-10-02.md` (the repo copy ends Thu 23:23 CEST)

## Monitoring plan for the next storm (Tue 6 Oct)

Each item fixes a gap from this run.

1. **Watch the TN10 stream/explorer as well as the REST API.** stp's memory of the earlier freeze is about the stream/explorer, and we had no data on it this time.
   - A websocket/block-stream lag sampler: subscribe to a public TN10 wRPC block stream and log, every 10 s, the newest block's DAA score and timestamp against n0's. Lag >60 s = stream stall.
   - Explorer page checks every 5 min on explorer-tn10.kaspa.org (latest blocks page): newest block time, HTTP status and load time.
2. **A mined-view watcher that restarts itself.** It crashed on restart at 01:00 this time and left a gap from 00:06 to 08:45. Run it under a supervisor loop or systemd (`Restart=always`), with a heartbeat line every sample and an alert after 2 missed samples.
3. **Address-specific API lag probes, light and logged.** Use 3–4 fixed addresses: stp's mining address, Grok Build's desk wallet, one runner lane and one quiet control address. One `full-transactions-page?limit=1` per address every 5 min, 20-s timeout. Save the full response (or its hash plus newest txid/time) so a "froze" claim can be checked later, unlike qp4jge this time.
4. **Block share per sampler, box and desk both tracked.**
   - Keep both the host sampler and the independent DAA-based sampler running.
   - Add a sanity check: if a share counter reads 0 while blocks flow, alert at once. After n0's restart this time it read 0 for all of L4 and silently disabled `mined_stall`.
   - Alert when the desk share drops to 0 while desk miners should be on.
5. **Inclusion vs submission per runner.** Log submitted, node-acked, rejected and included on the virtual chain for every runner and the desk sender, in one schema, every 10 s. That way the desk numbers can be measured instead of quoted.
6. **Measure fee recapture from coinbase outputs.** Sum the coinbase outputs to stp's mining address per block (from n0) and split them into subsidy and fees. That replaces the ~57% estimate.
7. **A timeline of disk, RAM and the prune window.** Every 60 s log free disk, RAM available, swap, load average, n0 data dir size and pruning point / prune-in-progress. Every leg this time ended on a disk or RAM guard, and starts were blocked during pruning.
8. **Sync the desk sender's logs to the repo during the run.** Push `sender.jsonl` and the status logs (`C:\Users\Fermi\kaspa-tn10\...`) to the private analysis repo every 15–30 min, so the desk side is never stuck on the desk PC again.
9. **Track third-party/covenant tx inclusion delay.** Every 30 s, take a light snapshot of n0's mempool: count and feerate histogram, plus for non-storm txs (not from our lane or runner addresses) the txid, script type (P2PK / P2SH / covenant-bearing outputs), first-seen time and fee. When each tx is included or evicted, log its pending time. That gives "stuck pending in the mempool" as a number. Keep it light: entries only, no address scans. Back off to every 2 min if a snapshot takes more than 2 s.
10. **A covenant-tx/hour counter.** From n0's accepted blocks (the block-added stream we already receive), count per hour the txs with covenant-bearing outputs or inputs that are not from our tooling. Log it next to box tx/s so "covenant tx/hour halved during the peak" can be checked. Start it at least 24 h before the storm for a baseline.
11. **Hard rule: no heavy address queries to n0 during the storm.** No UTXO-by-address scans or full-history calls against n0 while load is on. Light probes go to the public API (item 3). Anything heavy waits until the runners stop.

## Sources

- Box logs (stp's box, not published raw):
  - `artifacts/stress-tests/run/timeline.md` (event log, read in full)
  - `data/runner1-4.out`, `data/p2w1-8.out`
  - `data/host.jsonl`
  - `data/api-health-min.jsonl`, `data/api-mined-watch.jsonl`, `public-api-calls.log`
  - `run/final-numbers-2026-10-02.md`, `run/GO-next-leg.md`
  - `feerate.jsonl` (n0 fee estimate and our feerate every 30 s)
  - n0 kaspad log `rusty-kaspa.log`
  - `artifacts/kaspa-tn10/share.csv` (independent share sampler)
  - `artifacts/kns-tn10/*`
- Private analysis repo (STP-KAS/tn10-storm-2026-10-analysis): `analysis/BOX-REPORT.md`, `analysis/desk-public-read-2026-10-02.md`, `desk/sender.jsonl`.
- Earlier test, private note STP-KAS/tn10-indexer-stall-2026-09 (commit `22780de`): `README.md` l.7–9, 12–14, 30, 33–36; `evidence/api-health-2026-09-29.txt` l.3. Box file `artifacts/stress-tests/dryrun/api-health-min-dry.jsonl` l.2 (first healthy sample, 1 Oct 18:27:39 CEST).
- Public data:
  - `api-tn10.kaspa.org/transactions/count/2026-10-0{1,2,3}`, saved in `data/sources/`
  - `api.kaspa.org/info/fee-estimate`, `/info/price`, `/info/blockdag`
  - Kraken `0/public/Ticker?pair=KASUSD|KASEUR`
  - rusty-kaspa source at commit [01b532e](https://github.com/kaspanet/rusty-kaspa/tree/01b532e8b553523216471682649693af92f0fd16) and [PR #1004](https://github.com/kaspanet/rusty-kaspa/pull/1004)

## Conclusion

- **Volume:** 58.9M box transactions included in four legs, 152 rejects, 361,814 tKAS in fees. Best minute 4,253 tx/s, best 10 minutes 3,717, best hour 2,518.
- **~5k TPS:** not reached as unique included transactions. Only meters that double-count (n0 "processed") or single 10-s steps get there or past.
- **What limited it:** block mass, per-connection submit rate, and above all one box's disk and RAM. Every leg ended on a disk or RAM guard. Our own hashrate decided how many of our txs got in.
- **Mining share:** stp's share was 50–63% while his box miners ran, and 25% over the first night. 60–70% is not supported. On TN10 an estimated ~57% of the fees came back to him.
- **The public API is the weak point, but it recovered much better than last time.** Thursday it lagged up to ~12 min. Friday night its indexer froze for about 85 minutes (HTTP 503) and the address view of stp's mining address froze with it, while n0 stayed synced. Every stall came under high load (not exactly at our peaks). Each one we could watch to its end cleared within 2–5 minutes of its last bad sample. In the 25 Sep test the same API's indexer stayed frozen for at least 3 days 15 hours. The stream/explorer view was not monitored in either test.
- **Mainnet, plain cost with nothing back:**
  - The whole test at 100 sompi/g is 45,464 KAS (~USD 1,929). At 150 sompi/g it is 68,195 KAS (~USD 2,894).
  - Holding the measured 1-min peak with the same light txs for 24 h is ~236,927 KAS (USD ~10,053) at normal, or ~355,390 KAS (USD ~15,079) at priority.
  - Mainnet could carry that rate with those txs. With properly signed txs it could not: the cap is ~2,854 tx/s.
