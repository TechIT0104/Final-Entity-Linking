# TR2016 Live Status (Autonomous Mode)

Date: 2026-04-20

## Current Outcome

- Official TR2016 source has now been identified and validated for download.
- TR2016 paper reproduction remains blocked on remote servers until those real files are copied into place.
- GPU usage is confirmed and functioning on server `172.20.70.80` for the evaluator path.

## Source Discovery (Resolved)

Authoritative chain recovered from Tsai & Roth (NAACL 2016) publication metadata:

- Publication backend: `https://cogcomp.seas.upenn.edu/page/publication_view/view-backend.php?id=785`
- Dataset resource backend: `https://cogcomp.seas.upenn.edu/page/resource_view/view-backend.php?id=102`
- Direct dataset zip: `https://cogcomp.seas.upenn.edu/Data/ccgPapersData/ctsai12/xlwikifier-wikidata.zip`

Local validation completed:

- Archive downloaded successfully (`__xlwikifier_wikidata.zip`, ~268 MB).
- Contains 12-language data tree: `data/{ar,de,es,fr,he,it,ta,th,tl,tr,ur,zh}/{train,test}`.
- Contains `*.txt` + `*.mentions` files (no `*.mentions.new`), so a conversion/copy step is needed before remote evaluation.

## GPU Proof (Resolved)

From long probe run (`__monitor_full_gpu_run.py`):

- Remote log path: `/DATA/kmpooja/mrefined_option1/logs/tr2016_gpu_fullprobe_20260420_140059.log`
- Evaluator log includes explicit device line:
  - `Refined device: cuda:0; cuda_available=True`
- GPU telemetry showed large allocations during startup/inference preparation:
  - memory climbed to ~13.9 GiB and non-zero utilization spikes (including 95-100%).
- Process completed one placeholder pass and exited normally.

## Dataset Evidence (Blocking)

Remote exhaustive scans found only placeholder files:

- `/DATA/kmpooja/mrefined_option1/assets/tr2016/de/test/placeholder.txt`
- `/DATA/kmpooja/mrefined_option1/assets/tr2016/de/test/placeholder.mentions.new`
- `/DATA/kmpooja/mrefined_option1/assets/tr2016/es/test/placeholder.txt`
- `/DATA/kmpooja/mrefined_option1/assets/tr2016/es/test/placeholder.mentions.new`
- `/DATA/kmpooja/mrefined_option1/assets/tr2016/fr/test/placeholder.txt`
- `/DATA/kmpooja/mrefined_option1/assets/tr2016/fr/test/placeholder.mentions.new`
- `/DATA/kmpooja/mrefined_option1/assets/tr2016/it/test/placeholder.txt`
- `/DATA/kmpooja/mrefined_option1/assets/tr2016/it/test/placeholder.mentions.new`

Server `172.20.70.170` has no `.mentions`/`.mentions.new` files in scanned roots.

## Autonomous Recovery Running

Background terminal ID:

- `2afea4af-b0f6-4d66-a976-7f8abb004fe7`

Command:

- `python tr2016_autonomous_runner.py --interval-sec 300 --watchdog-interval-sec 120 --watchdog-max-restarts 8`

Behavior:

- Polls remote dataset health every 300s.
- If real data appears for all required languages (`de/es/fr/it`), it auto-runs `tr2016_autorecover_watchdog.py`.
- Watchdog handles failures/restarts and writes state to `tr2016_watchdog_state.json`.

## Files Added/Updated in This Session

- `tr2016_autonomous_runner.py` (new)
- `TR2016_LIVE_BLOCKER_STATUS.md` (this file)

Already-existing runtime state files used:

- `tr2016_watchdog_state.json`
- `tr2016_watchdog_events.log`
- `tr2016_autonomous_runner_state.json`
- `tr2016_autonomous_runner.log`

## What Must Exist for Final Valid TR2016 Results

Under `/DATA/kmpooja/mrefined_option1/assets/tr2016/`:

- `de/test/*.txt` and matching `*.mentions.new` or `*.mentions`
- `es/test/*.txt` and matching `*.mentions.new` or `*.mentions`
- `fr/test/*.txt` and matching `*.mentions.new` or `*.mentions`
- `it/test/*.txt` and matching `*.mentions.new` or `*.mentions`

Once these are present, autonomous execution is already armed and will proceed without manual intervention.
