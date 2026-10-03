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
| Public API under load | Lagged up to 11.7 min on Thursday, and **froze for about 85 min** on Friday night (HTTP 503) | `data/api_*.csv` |
| Mainnet cost of the whole test, same txs at 100 sompi/g | **45,464 KAS** (USD 1,929). At 150 sompi/g: 68,195 KAS (USD 2,894) | `data/mainnet_actual_test.csv` |

## What

stp's box node **n0** (rusty-kaspa kaspad 2.1.0, TN10, one 8-core Xeon VM with 15 GB RAM and a 126 GB disk) was loaded by our own index-free runners in four legs. Grok Build sent extra load from stp's desk PC through public TN10 nodes, using the wallet `kaspatest:qp4jge54…`.

- **Runners.** At first these were "SMX": signed 1-in-1-out P2PK hops of about 1,752 g. From Thu 21:42 they were "P2W": unsigned 1-in-1-out hops between pay-to-script-hash lane addresses whose redeem script is `push4(id) OP_DROP OP_TRUE`, about 643 g each (`storm-p2w-runner.mjs`). P2W outputs are **anyone-can-spend**. That was fine for throwaway testnet coins. It matters for the mainnet section.
- **Funding.** The runners were funded from the coinbase outputs of stp's TN10 mining address `kaspatest:qzffl5…`.
- **Fees.** The feerate was a multiple of n0's own fee estimate. It was 3× and floating until Fri 00:10, a fixed 6,000 sompi/g (30×) for 24 minutes, then a flat 2× capped at 400 sompi/g.

## Why

There were three goals:

- Find the ceiling of one box plus stp's hashrate on TN10.
- See whether the public explorer/API view of mined blocks breaks during a storm.
- Learn what such a storm costs in fees.

## When

| Leg | Window (CEST) | What happened | Box included | Fees (tKAS) |
|---|---|---|---:|---:|
| **L1** | Thu 1 Oct 20:35:18 → Fri 07:52:54 | SMX ramp, then P2W. RAM STOP 23:13, planned pause 00:10–01:10 for an n0 rebuild, **30× fee 01:10–01:27**, box miners halted 01:31:50, then ~300 tx/s all night. RAM STOP 07:52:54 | 29,884,172 | 291,967 |
| **L2** | Fri 09:07:39 → 10:15 | 6 P2W runners, flat 2× fee. 09:43: 4 RPC connections per runner lifted rate from ~2,260 to ~2,900 tx/s. Disk pause at 19.5 GB from ~09:55. Box rebooted 10:15 | 6,815,084 | 14,811 |
| **L3** | Fri 11:49:49 → 16:50:47 | Knee test: 6 runners 2,410 tx/s, 7 runners 2,383 (flat), 8 runners **collapsed to 1,165** (12:11, blocks mass-full at 492k, mempool 14k→79k). Disk pause from 13:03:41. Disk STOP 16:50:47 | 8,188,106 | 20,239 |
| **L4** | Fri 21:52:07 → Sat 01:06:29 | n0 without utxoindex. 6 runners, flat 2×. Best 5 min 3,258 tx/s (23:15). RAM/sink-age back-offs 23:30 and 23:44, then ~0. Hard abort on sink age 10.1 s at 00:29:55. Disk STOP 01:06:29 | 14,018,548 | 34,797 |
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
  - Then per-process submit throughput, about 380–850 tx/s per runner over one RPC connection.
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

†Box miners' accepted submits divided by DAA growth. The "all blocks through n0" column gives 52.6%. The two independent samplers agree within 2 points in L1–L3.

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

- **Thursday (L1): lag, not a freeze.** The indexer fell up to 11.7 min behind. The mined-coinbase view lagged up to 10.9 min. 28 HTTP 503s, 22 of them with the DB reporting `isSynced:false`. It recovered once load dropped.
- **Friday night (L4): a full freeze of about 85 minutes (≈22:02–23:28).** From 22:05 the indexer lag grew by exactly ~120 s per 120-s sample. It got no further at all, and every health call from 22:09 to 23:27 returned **HTTP 503** with `isSynced:false`. The newest coinbase shown for stp's mining address froze at the same time: its lag grew from 89 s (22:04) to 4,138 s (23:19) and was back to 9 s at 23:29. Meanwhile n0 kept seeing stp's miners win ~50% of blocks (independent sampler), so the address view was stale, not quiet. ‡The sampler's own `mined_stall` flag missed this, because its "blocks we mined" input came from the host sampler's share counter, which read 0 after n0's Friday restart.
- **Address-level freezes.** The only address read on a schedule was stp's mining address (qzffl5). Its page timed out (20 s) 22 times across all windows, plus the L4 freeze above. Grok Build's wallet qp4jge was read 13 times on Fri 07:52–07:57. One `transactions-count` call needed a retry with a 60-s timeout. The first attempt's result was not saved, so **"qp4jge's view froze" is UNVERIFIED**. No other addresses were probed.
- **Measurement gaps:** mined-view watcher **Fri 00:06–08:45** (it crashed on restart at 01:00:31, so the 01:24 peak has no mined-view data) and 08:45–12:13. Health probe Fri 00:09–01:00, 08:44–09:07 and 10:13–11:49.
- n0 itself stayed synced throughout L1 (4,297 of 4,297 RPC polls; sink age max 3.1 s, private box report). In L4 a hard abort fired on a 10.1-s sink age (00:29:55).

### 5. Limits of this test (honest list)

- **One box.** 8 vCPU, 15 GB RAM, 126 GB disk, shared by n0, the box miners (nice 19), the runners and the samplers. The load average reached ~28–32 on 8 cores in L2 (timeline 09:19, 09:31).
- **Caps:**
  - Block compute mass: SMX filled blocks at ~285 txs. P2W at 6–8 runners pushed blocks to 492–499k g; in L3, adding the 8th runner made throughput fall.
  - Node submit throughput: ~380 tx/s per runner over one wRPC connection, ~480 with 4 connections.
- **RAM:**
  - Two storm-watch STOPs at RAM below 1 GB: Thu 23:13:34 (1,009 MB; a read-only scan script contributed) and Fri 07:52:54 (754 MB; most likely a large outside read of qp4jge's mempool entries).
  - The coinbase feeder had to be restarted on RSS more than 10 times.
  - **n0 was OOM-killed at Fri 00:50** by one `getUtxosByAddresses` call on stp's mining address, which holds a huge number of coinbase UTXOs (kernel: kaspad anon-rss 9.46 GB).
- **Disk.** 4.5–7 GB/h at load. Every leg ended on disk: L1 at the 25 GB self-pause, L2 at 19.5 GB, L3 and L4 at the 21 GB pause and then a STOP after 15 min under 19 GB. The Fri 08:09 pruning low point was 9.15 GB.
- **Fee float feedback loop.** "3× the node's normal estimate" chased its own backlog: up to 19,244 sompi/g (Thu 23:56). The fixed 30× burned 122,320 tKAS (42% of L1 fees) in 24 minutes. A flat 2× then lost to outside senders while n0's normal estimate hit 24,145 (Fri 01:51).
- **Pruning windows.** The pruning-point move (Fri 07:51–08:30, and around 19:34–20:13) eats disk and RAM. Starts were blocked around 18:55–20:15.
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
3. **Policy.** Mainnet mempool policy accepts these shapes the same way TN10 kaspad 2.1.0 did. The minimum relay fee applies to compute/transient mass (PR #1004).
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
| KNS 18,524 names, ownership verified | 9,509 + 8,258 + 757 verified on api.knsdomains.org | ✅ |
| qp4jge 10.66M txs | Value from a logged API call; the raw response was not saved | ⚠️ attributed |

## Missing (needs files from stp's desk)

Grok Build's numbers for the Friday-evening run, and its desk log after Thu 23:23, are not on the box. To add the desk side of L4 and a full desk count, these files are needed (paths as written by the Build prompt):

- `C:\Users\Fermi\kaspa-tn10\build-storm2\final-report.json`: accepted, rejects, avg tx/s, spent, first/last txid
- `C:\Users\Fermi\kaspa-tn10\build-storm2\logs\` (status lines every 60 s)
- the full desk `sender.jsonl` behind `desk-public-read-2026-10-02.md` (the repo copy ends Thu 23:23 CEST)

## Sources

- Box logs (stp's box, not published raw):
  - `artifacts/stress-tests/run/timeline.md` (event log, read in full)
  - `data/runner1-4.out`, `data/p2w1-8.out`
  - `data/host.jsonl`
  - `data/api-health-min.jsonl`, `data/api-mined-watch.jsonl`, `public-api-calls.log`
  - `run/final-numbers-2026-10-02.md`
  - n0 kaspad log `rusty-kaspa.log`
  - `artifacts/kaspa-tn10/share.csv` (independent share sampler)
  - `artifacts/kns-tn10/*`
- Private analysis repo (STP-KAS/tn10-storm-2026-10-analysis): `analysis/BOX-REPORT.md`, `analysis/desk-public-read-2026-10-02.md`, `desk/sender.jsonl`.
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
- **The public API is the weak point.** Thursday it lagged up to ~12 min. Friday night its indexer froze for about 85 minutes (HTTP 503) and the address view of stp's mining address froze with it, while n0 stayed synced.
- **Mainnet, plain cost with nothing back:**
  - The whole test at 100 sompi/g is 45,464 KAS (~USD 1,929). At 150 sompi/g it is 68,195 KAS (~USD 2,894).
  - Holding the measured 1-min peak with the same light txs for 24 h is ~236,927 KAS (USD ~10,053) at normal, or ~355,390 KAS (USD ~15,079) at priority.
  - Mainnet could carry that rate with those txs. With properly signed txs it could not: the cap is ~2,854 tx/s.
