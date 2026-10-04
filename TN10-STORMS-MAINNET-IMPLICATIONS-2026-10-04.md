# TN10 storms and stress tests: what they do and do not say about a mainnet storm

**Written Sun 4 Oct 2026 by Grok Bot for stp. Kaspa Testnet-10 (TN10) only. Nothing in any of these tests touched mainnet.** All times are CEST (UTC+2) unless marked Z/UTC. This doc re-reads the existing storm write-ups and their logs and labels every statement about mainnet. File paths name the source file: files under `data/` are in this repo; the others are logs and notes on the operator's test box or in other STP-KAS repos, and most raw logs are not public.

Every statement about mainnet in this doc carries one of three labels:

| Label | Meaning |
|---|---|
| **A** | **Shown on TN10.** Backed by our own measured data. The number and the file it came from are given. An A label is about TN10 only. It never means "proven for mainnet". |
| **B** | **Plausible for mainnet, but unsure.** The reason it might not carry over is given. |
| **C** | **Unknown.** Needs more testing and review. The test that would settle it is given. |

Mainnet protocol inputs (block rate, mass limits, relay floor) were read from rusty-kaspa source and the live public mainnet API. They are inputs, not storm results, so they are listed separately in [Reference inputs](#reference-inputs-not-storm-results) and are not labelled A.

---

## Summary (plain sentences)

1. No TN10 result in our storms is proven for mainnet. TN10 differs from mainnet in hashrate (about 7 billion times smaller), in who mines, in node count and peer diversity, in fee demand, and in the state of its UTXO set. Our tests also ran through one node (n0) on one small box.
2. What is well shown on TN10 (A): once enough senders ran, **block mass was the ceiling**. Our box got **58,905,910** transactions included in four legs on 1–3 Oct. Its best minute was **4,253 tx/s**, best 5 minutes **3,843–3,850**, best hour **2,518**. Adding more workers past the knee made things worse: on 2 Oct, 6 workers gave **2,410**, 7 gave **2,383**, 8 collapsed to **1,165**.
3. The "~3,000 tx/s with 6 workers on 2 Oct" figure is real (scaler readings **3,024** and **3,025** at 23:16 and 23:23 CEST), but it is **not the overall peak**. That came on 2 Oct at 01:21–01:26 with 7 workers, a 30× fee and our miners on.
4. **About 4k tx/s combined with stp's desk build is stp's report, not our measurement** (C). No desk transaction was matched against n0, and the public indexer was frozen during the overlap.
5. The September "6.5k–12k TPS" figures came from kaspad's "Processed" counter. That counter counts a transaction once per block body, and one transaction can sit in several parallel blocks. On TN10 it overstated unique throughput by about a third (B/A = 1.337, round 7). Unique September throughput is unknown.
6. **On TN10 our own hashrate decided how many of our transactions got in.** When our box miners stopped (2 Oct 01:31:50), our inclusion fell to about 300 tx/s while blocks were only 11–26% full. On mainnet a storm sender would usually have no meaningful hashrate. Whether other miners would pick up and include a flood at the same rate is **unknown** (C).
7. Mainnet cost tables (45,464 KAS for the whole test at 100 sompi/g; about 237k KAS for 24 h at the 1-minute peak) are **arithmetic, not measurements** (B). They assume the floor fee is enough to get in, no fee war, mainnet relay policy accepting the same transaction shapes, a fixed price, and no fee coming back. The cheap 643-gram shape we used is anyone-can-spend, so a real mainnet attacker could not use it safely. Signed transactions cap at about **2,854 tx/s**.
8. **The September write-ups priced mainnet with a 1 sompi/gram relay floor. That is outdated.** rusty-kaspa PR #1004 (merged 15 May 2026) raised it to 100 sompi/gram, and the live mainnet estimate read 100 on 2 and 3 Oct. Those "24 KAS per 10 minutes" figures are about 100× too low.
9. What broke first on TN10 was not consensus. It was **our box** (disk, RAM), the **public TN10 indexer** (api-tn10 froze for 86 minutes on 2 Oct and for at least 3 days 15 hours after 25 Sep), and our node's **pruning disk use** (the 3 Oct crash). How much of that applies to mainnet nodes and mainnet APIs is mostly **unknown** (C).
10. More testing is needed before anyone says "a mainnet storm would do X". The highest-value tests are in [Open questions](#biggest-open-questions-and-the-tests-that-would-settle-them).

---

## The big differences between our TN10 tests and mainnet

| Factor | Our TN10 tests (measured) | Mainnet (what we know) | Why it matters for any mainnet claim |
|---|---|---|---|
| **Hashrate** | TN10 47.8 MH/s at 2 Oct 07:45 UTC (`analysis/desk-public-read-2026-10-02.md` §3) | 338,836.66 TH/s at the same read (same file). About 7×10⁹ times TN10 | Mining share, fee recapture and "who includes the flood" do not transfer |
| **Our mining share** | 50–63% of blocks n0 saw while our box miners ran; 0.6% after they stopped; 25.1% over leg 1 (this repo's `README.md` §3, `data/block_share_*.csv`) | A storm sender would normally have ~0% | On TN10 our miners mostly included our own txs. On mainnet nobody does that for the attacker |
| **Fee recapture** | Round 7 measured our miners collecting **85% of all fees with 53% of blocks** in a 10-min window (`tn10-vprogs-round7-ideas/README.md` l.79–93). Oct storm estimate 56.6% (inference, public report §3) | 0 for a sender with no hashrate (protocol logic, not tested) | TN10 net cost was much lower than gross. Mainnet bills must use gross |
| **Node count and peer diversity** | One node of ours (n0, `--outpeers=6 --maxinpeers=24`, break-test `logs/round4/n0-resync-2026-10-03.md`). Five public TN10 kaspad 2.1.0 nodes seen on 2 Oct (muon, vector, proton, neutrino, boson), holding very different mempools at the same moment (34,684 to 401,448 at 07:10 UTC; private desk notes, 2 Oct) | Not measured by us. Mainnet node count is unknown in our data | Propagation of a flood across many independent nodes was never tested |
| **Block rate** | About 10 blocks/s: 10.85 blocks/s in round 7 (README l.71); 10.9 blue steps/s on api-tn10 (desk read §1) | 10 blocks/s in `MAINNET_PARAMS` (rusty-kaspa `01b532e`) | Similar. This is the one factor that lines up well |
| **Our box (n0)** | 8 vCPU, 16 GB RAM, 126 GB disk shared by n0, miners, runners, samplers (public report, Hardware used). `--ram-scale=0.1` (mempool cap 100k vs default 1M) | Real nodes vary | Every Oct leg ended on our own disk or RAM guard, not on a network limit |
| **Disk pause** | Runner disk-pause line 21 GB at the L2 start (09:09), lowered to 19.5 GB at 09:24, back at 21 GB in L3: storm paused at ~20.9 GB free from 13:03:41 on 2 Oct; disk STOPs at 16:50:47 and 3 Oct 01:06:29 (`run/timeline.md`) | n/a | Throughput figures are capped by our disk, not by Kaspa |
| **RAM / OOM** | n0 OOM-killed 2 Oct 00:50:22, kaspad anon-rss 9.46 GB, after one `getUtxosByAddresses` on our mining address with 2.73M UTXO entries (`timeline.md` l.77; break-test `HANDOFF.md` 2 Oct 00:13–00:59 section) | Untested | A node-operator risk on any network, but our trigger was our own heavy query |
| **Pruning disk crash** | 3 Oct: free disk 13,017 MB (07:49:36) → 1,718 MB (07:54:04), steepest 30-s steps ≈1.6 GB (≈3.2 GB/min); watchdog SIGINT 07:53:46, SIGSTOP 07:56:04 (break-test `logs/round4/n0-disk-watchdog.log`) | Untested | Pruning cost depends on UTXO set size and disk headroom |
| **Spam-bloated UTXO set** | 322.4M UTXOs at the 29 Sep resync (HANDOFF l.223); 324.72M at the 3 Oct resync (`logs/round4/n0-resync-monitor.log`) | Not measured by us | TN10's UTXO set is shaped by months of test spam and coinbase dust |
| **Submitting machines** | One box (runners on localhost) plus stp's desk PC through public nodes | An attacker could use many machines | Our per-connection and per-box ceilings are not network ceilings |
| **Fee market / demand** | Quiet TN10 baseline ≈54.9 regular tx/s (the baseline used in the desk read); our storm set the fee level | Mainnet ≈1.07 regular tx/s over 31 h on 1–2 Oct (desk read §1) | No real competing demand was present in either case. A fee war was never modelled |
| **kaspad versions** | api-tn10 backends answered as 2.0.1 on 16 and 2.1.0 on 34 samples on 1 Oct (`analysis/REPORT.md` l.62); one read said 2.0.0, then 2.1.0, on 2 Oct (desk read §2) | Mainnet mix not measured | Public-API behaviour mixed different node versions |
| **Meters** | Box counts unique txids on n0's virtual chain. kaspad "Processed" counts per block body (overstates by ~1.34×). Desk `accepted` is a submit result | n/a | Several published "TPS" numbers are not unique inclusion |

---

## Reference inputs (not storm results)

| Input | Value | Source |
|---|---|---|
| Mainnet block rate | 10 blocks/s | rusty-kaspa `01b532e`, `consensus/core/src/config/params.rs` (quoted in `analysis/mainnet-cost.md` §1) |
| Block mass limits | compute 500,000, storage 500,000, transient 1,000,000 | same |
| Minimum relay fee | 100 sompi/gram | `mining/src/mempool/config.rs`; rusty-kaspa PR #1004, merged 2026-05-15 12:28:59Z (re-checked on GitHub 4 Oct 2026) |
| Live mainnet fee estimate | 100 sompi/g on every bucket | `api.kaspa.org/info/fee-estimate`, 2 Oct 07:45 UTC (desk read §3) and 3 Oct 15:54/15:58 UTC (public report, mainnet section) |
| Capacity by shape (compute mass ÷ 500k × 10/s) | 643–645 g P2W hop: ~7,754–7,770 tx/s. 1,624 g standard payment: 3,070 tx/s. ~1,752 g signed SMX hop: ~2,854 tx/s | desk read §2, public report mainnet section |
| Mainnet demand | ~1.07 regular tx/s (31 h, 1–2 Oct) | desk read §1 |

---

## One section per storm or test

### 1. TN10 farm mining stress, 18–21 Sep 2026
- **Setup:** dedicated TN10 kaspad, up to 150 one-thread CPU miners (~9 MH/s), bore tunnel, `--rpcmaxclients=400`.
- **Measured (A, TN10):** IBD stuck at ~99% headers on one peer until restart; tip-chase loops; `RouteIsFull` on `SubmitBlock` under farm load (≈28k found, ≈28k route_full, ≈250 submit_ok in the last window); one datadir LOCK panic; multi-hour utxoindex resync. Sources: `FULL-AUDIT-TN10-stress-and-threats.md` §A–E, `TKAS-mining-grok-bot-review-2026-09-20.md`.
- **Mainnet:** consensus isolation of the two networks is protocol fact. Whether the IBD stuck-peer and RPC backpressure issues show up on mainnet nodes: **B** (same code paths) / **C** (needs a mainnet operator report or a reproduction under mainnet-like peer counts).

### 2. Break test / round 1 overload, 25 Sep 2026, 21:48:41–22:46:14
- **Setup:** n0 alone, kaspad 2.1.0, `--ram-scale=0.1` (mempool cap ~100k), 8 P2SH workers at 1.2× the 100 sompi/g floor; fee-tier probes every 30 s.
- **Measured (A, TN10):** kaspad "Processed" counter averaged **6,466 tx/s** (10-s peak 9,274) (break-test `findings/overload-30m-summary.md`, from `logs/tps12h/nettps.jsonl`; `scripts/nettps.sh` reads the Processed line, so this is all senders and per block body). Mempool hit 99.97k; 30,298 evictions by feerate; no panic in the window (one panic at 21:12 at `100001 > 100000`). Probes: 1× floor p50 7.0 s, max 105 s; 10× max 3.7 s; 100× no better than 10×.
- **Mainnet:** fee priority protecting higher-fee users: **B** (same mempool ordering code; but one node, own flood, tiny cap). The "24 KAS per 10 min" mainnet estimate in that file is **wrong** (used a 1 sompi/g floor; see corrections). Unique September throughput: **C**.

### 3. Rounds 2–6, 25–26 Sep 2026
- **Round 2** (22:47 25 Sep–06:31 26 Sep): network 10-s samples median 1,548, mean 2,507, peak 12,175 (Processed counter; `grok-bot-vprogs-round2/README.md`). Ended on a disk taper at 9.5→8.4 GB. ~197,800 tKAS fees.
- **Round 3:** vprogs under storm; upstream tic-tac-toe finished 5 games under full storm; own guest executed 0 impossible debits (exec mode, proofs off) (`grok-bot-vprogs-round3/README.md`; `tn10-vprogs-final-verdict/README.md`).
- **Round 4** (26 Sep): paced 6× fee run, **1,219 accepted tx/s for 1 h 32 min** (07:46:20–09:18:15), ~6.7M txs; pruning/compaction needed >15 GB transient disk (`grok-bot-vprogs-round4/README.md`).
- **Round 5** (09:22–10:35): own index-free runners, 1,036,520 accepted of 1,039,575; storm fees at 20,000–60,000 sompi/g (`round5/README.md`).
- **Round 6** (10:35–13:16): **10,058,024 accepted in ~159 min**, ~1,191 tx/s full-gusto, ~1,057 whole round (`round6/README.md`).
- **Mainnet:** none of these rates is a mainnet capacity statement. They are what one box pushed through n0 on TN10 (A for TN10 only). vprog client behaviour under a mainnet fee market: **C**.

### 4. Round 7 measurements, 26 Sep 2026
- **Measured (A, TN10):** three TPS columns over 20 min: unique selected-chain accepted **267.2/s**, Processed block-body **357.2/s** (B/A **1.337**), our senders 205.0/s. Fee window: our miners took **85% of fees with 53% of blocks**; net fee cost −63 tKAS (`tn10-vprogs-round7-ideas/README.md` l.64–93).
- **Mainnet:** the 1.337 ratio depends on DAG width at that load: **B**. Fee recapture does not apply to a no-hashrate sender: **B** (protocol logic; not tested).

### 5. api-tn10 indexer stall, 25 Sep 2026
- **Measured (A, TN10):** api-tn10 stopped advancing accepted txs at 21:55:38 CEST and still returned HTTP 503 on 29 Sep 12:56 CEST (≥3 d 15 h) (the 25 Sep indexer-stall note). Cause unproven.
- **Mainnet:** whether api.kaspa.org or mainnet explorers would stall under a similar flood: **C**.

### 6. Pruning outages and resyncs, 26 Sep–3 Oct 2026
- **27 Sep (A):** pruning-point UTXO verification took ~13.3 GB temp disk (free 16.6 → 3.2 GB) and the watchdog stopped n0 (HANDOFF, 27 Sep 19:45 entry). 26 Sep 07:07–07:10: pruning/compaction grew consensus data about 75 → 89 GB and free space reached zero (`grok-bot-vprogs-round4/README.md` l.39).
- **29/30 Sep resync (A):** pruned resync after a reboot. UTXO set download 22:47:49 → ~23:17 (~29 min), **~322.4M UTXOs**; miners started 30 Sep 00:25, about **2 h** after the 22:25 start (HANDOFF l.221–224).
- **3 Oct crash and resync (A):** disk drop described above; n0 frozen at 1.5 GB free. Wipe of the 110 GB datadir at 09:54:49; headers done 10:44:38; UTXO download from one peer at only **~0.48M UTXOs/min** (box idle, peer had 3.9 s ping); restart with `--connect` to three ~100 ms peers at 11:23:18 gave **~10M/min**; synced **13:22:39** (~3 h 28 min after start), set **324.72M UTXOs**, DB 70 GB (HANDOFF 3 Oct section; `logs/round4/n0-resync-monitor.log`).
- **Mainnet:** pruning disk spikes and slow single-peer IBD are node behaviours that could matter on any network: **B**. Their size on mainnet depends on mainnet's UTXO set and peers: **C**.

### 7. Box storm, 1–3 Oct 2026 (legs L1–L4)
Sources: this repo's `README.md` (data in `data/legs_box.csv`), `run/final-numbers-2026-10-02.md`, `run/timeline.md`, `analysis/BOX-REPORT.md`.

| Leg | Window | Included (box, unique) | Fees tKAS | Key events |
|---|---|---:|---:|---|
| L1 | 1 Oct 20:35:18 → 2 Oct 07:52:54 | 29,884,172 | 291,967 | 30× runner segment 01:09:58–01:33:41; best 5 min 3,850 (01:21:20, 7 runners); miners halted 01:31:50; then ~295 median |
| L2 | 2 Oct 09:07:39 → 10:15 | 6,815,084 | 14,811 | best 5 min 2,913; disk at the 19.5 GB pause line ~09:55; box reboot 10:15 |
| L3 | 2 Oct 11:49:49 → 16:50:47 | 8,188,106 | 20,239 | knee test; disk pause 13:03:41; STOP 16:50:47 |
| L4 | 2 Oct 21:52:07 → 3 Oct 01:06:29 | 14,018,548 | 34,797 | 6 runners; scaler 3,024 / 3,025; best 60 min 2,518; RAM/sink-age back-offs; disk STOP |
| All | | **58,905,910** | **361,814** | 152 rejects |

- **Measured (A, TN10):** best 1 min 4,253 (2 Oct 01:24:46); n0 stayed synced on all 4,297 polls in L1, sink age max 3.1 s (BOX-REPORT l.147–148); block compute mass 30-min means up to 92.8% (BOX-REPORT l.91); mempool peak 99,992; n0's normal fee estimate peaked at 24,144.8 sompi/g (01:51:21) because of our own backlog; public API lag up to 704 s on 1 Oct and an 86-min freeze on 2 Oct ≈22:02–23:28.
- **Mainnet:** see claims table. Rates are TN10-only (A); mainnet capacity arithmetic is B; real mainnet handling is C.

### 8. Knee test and the 6-worker reading, 2 Oct 2026
- **Measured (A, TN10):** L3 knee (`timeline.md` 12:02–12:25 entries; `build-brief-how-box-storm-works-2026-10-02.md` §7): N=6 **2,410**, N=7 **2,383** (flat), N=8 **1,165** (mempool 14k → 79k in 75 s, blocks 492k mass, block rate 9.1 → 7.8/s). L4 scaler at N=6: **3,024** (23:16:52) and **3,025** (23:23:53) (`timeline.md`, scaler lines). Overnight in L1, 7 runners gave the best reading (3,845 at 01:26:22), and the 01:33 "N=8 = 782" break point was the miner halt, not the 8th runner (`timeline.md` 01:46:39 entry).
- **What this means:** "7–8 workers lowered throughput" is true for L3 (7 flat, 8 collapsed), not as a general rule. The knee moved with fee level, miner state and outside traffic.
- **Mainnet:** the knee is a property of our box, our pacing and TN10 block mass with our miners on: **C** for mainnet.

### 9. Desk side (Grok Build on stp's PC) and the 2 Oct gusto drains
- **Measured, desk logs (A as submit counts only):** 17,415,510 submits, 15,743,212 in the `accepted` field (a submit result, not inclusion); highest printed P2W virtual-chain minute 2,795.6 (2 Oct 21:33); submit-ok status lines up to 24,249/s, which is above every block ceiling, so not inclusion (public report, Desk check).
- **Gusto drains, 2 Oct (from private GitHub notes, not re-measured):** one public node (muon-10), about 112–240 tx/s accepted, sends paused at mempool 85k (private desk notes, not public).
- **~4k tx/s combined (box + desk): stp's report. Not measured by us. C.** No join of desk txids against n0; the indexer was frozen for most of L4.

---

## Claims table

| # | Claim | Label | Evidence or reason | Test needed |
|---|---|---|---|---|
| 1 | On TN10, block mass was the throughput ceiling once enough senders ran | **A** | L3 knee: 8 runners pushed blocks to 492k mass and throughput fell to 1,165 (`timeline.md` 12:13:53; `build-brief…` §7); compute mass up to 92.8% (BOX-REPORT l.91) | — |
| 2 | Mainnet would hit the same block-mass ceiling at the same tx shapes | **B** | Same consensus limits in source. But mainnet has many more nodes, real miners and other traffic; propagation and template building at that load were never tested | Multi-node storm with independent miners; measure per-block mass and unique inclusion |
| 3 | Our box got 4,253 tx/s best minute, 3,843–3,850 best 5 min, 2,518 best hour (unique inclusion) | **A** | `data/legs_box.csv`; `final-numbers-2026-10-02.md` | — |
| 4 | Mainnet "can do ~4,000 tx/s" | **C** | Only capacity arithmetic exists (7,754/s for a 645 g anyone-can-spend hop; 2,854/s signed). Real mainnet propagation, mempools and miners at that rate are untested | Multi-node, multi-region test with miners we do not control, unique-inclusion meter |
| 5 | 3,024–3,025 included tx/s with 6 workers on 2 Oct | **A** | `timeline.md` scaler 23:16:52 and 23:23:53. Not the overall peak (claim 3) | — |
| 6 | 7–8 workers lower throughput | **A** (L3 only) | N=7 2,383 vs N=6 2,410; N=8 1,165. In L1, N=7 was the best (3,845) | Repeat the knee at fixed fee, miners on/off, outside load logged |
| 7 | The same knee would apply to a mainnet sender | **C** | Knee depends on our box CPU/RAM, pacing, n0's 100k mempool cap and our own miners | Knee test from a separate sender box against several nodes, default mempool cap |
| 8 | ~4k tx/s combined box + stp's desk | **C** | stp's report. No desk txid join; indexer frozen during L4; desk meters are submit counts | Same-schema logging on both senders and a txid join against one node's virtual chain |
| 9 | "~5k TPS" as unique inclusion | **A (not supported)** | Box max 4,253/min; only the double-counting Processed counter and 10-s steps go higher (public report §"The ~5k TPS question") | — |
| 10 | September "6.5k / 12k TPS" were included throughput | **A (not supported)** | `scripts/nettps.sh` reads kaspad's Processed line (all senders, per block body). Round 7 measured Processed/unique = 1.337 | Unique September rate stays unknown (C); logs lack per-txid acceptance |
| 11 | Paying ~10× the floor kept probes under 4 s during a flood | **A** | 117 probes per tier, 10× max 3.7 s (`overload-30m-summary.md`) | — |
| 12 | The same fee-priority protection would work on mainnet | **B** | Same mempool ordering code. But one node, own flood, 100k cap, no competing bidders | Probe test on a multi-node network with a second, competing high-fee sender |
| 13 | 100× fee buys nothing over 10× | **A** (TN10) / **C** (mainnet) | TN10 probes; mainnet fee war never modelled | Fee-war simulation with ≥2 bidders |
| 14 | Mainnet bill for the whole test: 45,464 KAS at 100 sompi/g | **B** | Arithmetic on verified params (`data/mainnet_actual_test.csv`). Assumes floor inclusion, no fee war, same relay policy, fixed price, no recapture | A mainnet fee-escalation model reviewed by core devs; cannot be tested on testnet |
| 15 | 24 h at the 1-min peak costs ~237k KAS (P2W shape) | **B** | Same assumptions, plus the rate was never held over ~1 h (best hour 2,518) | Hold a rate ≥4 h on TN10 with a stable box before extrapolating |
| 16 | September "24 KAS per 10 min" mainnet estimate | **Wrong (corrected)** | Used a 1 sompi/g floor. Floor is 100 sompi/g since PR #1004; corrected figure ≈100× higher, about 2,400 KAS per 10 min at 1.2× floor if the (unverified, Processed-counter) volume held | — |
| 17 | A mainnet attacker could use the 643 g P2W trick | **B (unlikely)** | P2W lanes are anyone-can-spend; anyone watching could take the lane coins. Signed shape is ~1,752 g, cap ~2,854 tx/s | Review of mainnet standardness and front-running risk |
| 18 | On TN10 our own hashrate decided inclusion | **A** (observation) | After miners halted at 01:31:50 on 2 Oct, inclusion ~300 tx/s with blocks 11–26% full (BOX-REPORT l.91; public report §5) | Cause is C: propagation, other miners' nodes or policy |
| 19 | Other mainnet miners would include a flood from a no-hashrate sender at TN10 rates | **C** | Never tested. TN10 evidence points the other way (claim 18) | Storm with zero own hashrate on a multi-node testnet; track which miners include it |
| 20 | Fee recapture ~57–85% | **A** (round 7, 85%) / **B** (Oct 56.6% estimate, inference) | Round 7 ledger2; Oct is fees × block share | Sum coinbase outputs per block during a storm |
| 21 | Mainnet sender with no hashrate gets no fees back | **B** | Protocol logic (fees go to the block's miner). Not a test result | — |
| 22 | n0 stayed synced and kept consensus under the storm | **A** | 4,297/4,297 polls synced, sink age max 3.1 s (BOX-REPORT l.147–148). L4 hard abort at sink age 10.1 s (00:29:55) | — |
| 23 | Mainnet nodes would stay synced under the same load | **B** | Same code. But different DAG history, more peers, no own miners feeding blocks | Load test on several nodes with diverse hardware |
| 24 | The public API is the first thing to fail | **A** (TN10 api-tn10) | 704 s lag (1 Oct), 86-min freeze (2 Oct), ≥3 d 15 h freeze (25 Sep) | — |
| 25 | api.kaspa.org / mainnet explorers would fail the same way | **C** | Different operators and infrastructure; no indexer logs | Ask indexer operators; replay load against a staging indexer |
| 26 | kaspad 2.1.0 panics at mempool 100,001 | **A** (with `--ram-scale=0.1`) | 25 Sep 21:12 on n0 (`findings/F1-mempool-assert-panic.md`). Later peaks near 100k evicted instead | — |
| 27 | Same panic risk on mainnet nodes at the default 1M cap | **B** | Same assert, larger cap; public TN10 nodes reported mempools of 34k–450k on 2 Oct in the desk notes, with no panic reported there; one desk note says public 2.1.0 has panicked past 100,000 (unverified by us) | Reproduce at default cap on a test node |
| 28 | Pruning-point moves can need 11–15 GB temp disk and grow the DB ~3 GB/min at peak | **A** | 27 Sep 13.3 GB temp (HANDOFF); round 4 >15 GB; 3 Oct watchdog log steps ≈1.6 GB/30 s | — |
| 29 | Mainnet pruning has similar disk spikes | **C** | Depends on mainnet UTXO set and node config; we do not run mainnet | Review with a mainnet node operator (read-only data) |
| 30 | Storm spam bloats the UTXO set and slows resync | **A** (TN10: 322.4M → 324.72M; resync 2 h to 3 h 28 min) / **B** (mainnet) | Our 1-in-1-out lanes add little; bloat on TN10 is mostly older spam and coinbase dust (our mining address held 2.73M UTXOs) | Measure UTXO count before/after a storm; separate lane, fan-out and coinbase outputs |
| 31 | Resync speed depends on the IBD peer | **A** | 0.48M UTXOs/min on one peer vs ~10M/min after `--connect` (3 Oct) | Mainnet IBD speed: C (operator data) |
| 32 | One 8-vCPU / 16 GB box is the bottleneck | **A** | Every Oct leg ended on our disk or RAM guard; load 28–32 on 8 vCPU (public report §5) | — |
| 33 | A better-provisioned attacker could go much higher on mainnet | **C** | Never tested beyond one box and one desk | Multi-box sender test with dedicated disks |
| 34 | ~378 tx/s per wRPC connection, ~1,046 with 3 connections | **A** (localhost) | `build-brief…` §4, §8 | Public-node and mainnet per-connection limits: C |
| 35 | Floor-fee users wait during a full-block storm | **A** (TN10: 1× p50 7 s, max 105 s) / **B** (mainnet) | Only if mainnet blocks actually fill, which needs claim 19 | — |
| 36 | Fee estimator chases its own backlog (3× normal reached 19,244 sompi/g; normal peaked 24,144.8) | **A** | public report §5; BOX-REPORT l.98 | Mainnet: B (same estimator code) |
| 37 | Third-party covenant txs got stuck and covenant tx/hour halved during the peak | **C** | stp's observation; tooling logged mempool size only | Mempool composition sampler + covenant counter (public report monitoring items 9–10) |
| 38 | TN10 runs at about mainnet's block rate | **A** (TN10 ≈10.85 blocks/s) | Round 7; desk read | — |

---

## Biggest open questions, and the tests that would settle them

1. **Would a flood from a sender with no hashrate be included by other miners at anything like TN10 rates?** (claims 18–19) Test: a storm on TN10 with all our miners off from the start, submitted to 3+ nodes we control in different regions, plus public nodes. Log per-txid first-seen on each node and which miner's block included it.
2. **Does block-mass saturation look the same with many independent nodes and miners?** (claim 2) Test: same as 1, plus per-block mass from several vantage points.
3. **What is the unique network-wide rate when two senders overlap?** (claim 8, stp's ~4k) Test: both senders log txids in one schema; join against one node's `virtual-chain-changed` accepted ids.
4. **How does a fee war change cost and user delay?** (claims 12–15) Test: two competing senders with different fee rules plus probe users; then a reviewed model for mainnet. Testnet cannot fully settle mainnet economics.
5. **Do our node failures (100k-cap panic, pruning disk spikes, OOM on big address queries) appear at default settings?** (claims 26–29) Test: a TN10 node on its own box with default `--ram-scale`, ≥500 GB disk, no heavy address queries during load.
6. **Would mainnet indexers and explorers stall?** (claim 25) Needs indexer-operator review; we have no indexer logs.
7. **How far could a better-provisioned sender go?** (claim 33) Test: two or more sender boxes, separate from the node box, against several nodes.
8. **How long can a storm be held?** Test: ≥4 h at a fixed rate on hardware that does not hit disk/RAM guards, so duration tables stop being extrapolation.

---

## Corrections found during this review

- **September mainnet fee floor (wrong):** the round-1/2 overload summaries and `overload-interim-2215.md` say mainnet's minimum relay feerate is 1 sompi/gram. It is 100 sompi/gram (PR #1004, merged 15 May 2026; live estimate 100). Their mainnet cost estimates are about 100× too low.
- **September "included TPS":** came from kaspad's Processed line (`scripts/nettps.sh`), which counts per block body and includes all senders. Not unique inclusion.
- **"3,024–3,025 tx/s peak":** correct as an L4 6-worker scaler reading; the overall box peak was 3,843–3,850 (5 min) and 4,253 (1 min) on 2 Oct 01:21–01:26.
- **"7 to 8 workers lowered throughput":** correct for the L3 knee only. In L1 seven workers gave the best reading; the first N=8 drop at 01:33 was the miner halt.
- **`analysis/REPORT.md` (1 Oct) is an interim** covering only the first ~2 h of samples; its "not beaten round 6" verdict is superseded by the later box report and public report.
- **Pruning-point move "~3 GB a minute":** the watchdog log supports about 2.5 GB/min average over 07:49:36–07:54:04 and ≈3.2 GB/min in the steepest 30-s steps on 3 Oct.

---

## Where these labels were applied

The same A/B/C labels were applied in place on 4 Oct 2026 to the files in STP-KAS repos that make mainnet claims about these storms: this repo (`README.md`, `methodology.md`), `grok-bot-vprogs-round1-public`, `grok-bot-vprogs-round2`, `tn10-vprogs-build-opinion`, `tn10-vprogs-grokbot-opinion`, and two private working repos. Files whose only mention of mainnet is a scope note ("TN10 only, nothing touched mainnet") were left as they were.

## Sources

Box logs and notes: `run/timeline.md`, `run/final-numbers-2026-10-02.md`, `build-brief-how-box-storm-works-2026-10-02.md`; the private analysis repo's `BOX-REPORT.md`, `REPORT.md`, `mainnet-cost.md` and `desk-public-read-2026-10-02.md`; this repo's `README.md` and `data/`; the break-test `HANDOFF.md`, `findings/`, `logs/round4/n0-disk-watchdog.log`, `logs/round4/n0-resync-monitor.log` and `scripts/nettps.sh`; the 25 Sep indexer-stall note; the round 1–8 repos and `tn10-vprogs-stress-findings`; the 18–21 Sep full audit of the CPU-farm test; private desk notes from 2 Oct; rusty-kaspa PR #1004 (read 4 Oct 2026).
