# Re-run the model across all datasets (GPU server)

This repo includes drivers to re-run the paper’s **best settings** across all datasets and write outputs into the expected folders under `results/<DATASET>/<RUN_NAME>/`.

## Security note
- Do **not** paste passwords into chat or scripts.
- Prefer **SSH keys** for server access.

## 1) SSH into the server (recommended: key-based)
On your local machine:

```bash
ssh-keygen -t ed25519 -C "mhel-llamo"  # press Enter for defaults
ssh-copy-id kmpooja@172.20.70.80        # installs your public key on the server
ssh kmpooja@172.20.70.80
```

If you must use password login, run:

```bash
ssh kmpooja@172.20.70.80
```

and type the password **manually** when prompted (do not script it).

If `ssh-copy-id` is not available on Windows, use WSL2, or manually append your public key to `~/.ssh/authorized_keys` on the server.

## 2) Prepare the repo on the server
On the server:

```bash
# Option A: copy the repo
# (run from your local machine)
# scp -r MHEL-LLAMO kmpooja@172.20.70.80:~/MHEL-LLAMO

# Option B: git clone (if you have a remote)
# git clone <YOUR_REMOTE_URL> MHEL-LLAMO

cd ~/MHEL-LLAMO
```

## 2.1) Probe the server (OS/GPU/conda/CUDA)
Run this on the server to print what we need to choose the correct install commands:

```bash
chmod +x ./server_probe.sh
./server_probe.sh
```

## 3) Create the two conda environments
The project recommends separate envs because BELA and the LLM stack can have conflicting deps.

```bash
conda create -n bela39 -y python=3.9
conda create -n llm -y python=3.9

conda activate bela39
pip install -r requirements_bela.txt

conda activate llm
pip install -r requirements_llms.txt
```

Notes:
- On Linux, CUDA-enabled torch is strongly recommended for the `llm` env.
- For FAISS, `conda install -c conda-forge faiss-gpu` (or `faiss-cpu`) may be easier than pip.

### Recommended CUDA PyTorch install (LLM env)
For text-generation you do **not** need `torchvision`. Installing it can sometimes cause the `torchvision::nms` runtime error.

```bash
conda activate llm
conda install -y pytorch torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
```

If you hit:

`RuntimeError: operator torchvision::nms does not exist`

Fix by removing torchvision from the `llm` env:

```bash
conda activate llm
pip uninstall -y torchvision || true
conda remove -y torchvision || true
python -c "from transformers import pipeline; print('transformers pipeline import OK')"
```

## 4) Authenticate to Hugging Face (if needed)
If the LLM repo is gated:

```bash
huggingface-cli login
# OR
export HUGGINGFACE_HUB_TOKEN=...  # preferred over passing --hf_token
```

## 5) Run the full best-settings rerun
This runs:
1) BELA candidate retrieval for each dataset (`get_candidates.py`)
2) LLM prompting (`filter_and_prompt_chain.py` / `filter_and_prompt.py`) into the *expected run folders*
3) Evaluation (`eval.py`)
4) Honest tables (`honest_eval_report.py`)

```bash
bash ./rerun_all_best_settings.sh
```

Optional env vars:

```bash
export DEVICE=cuda:0
export TOP_K=50
export BATCH_SIZE=4
export FORCE_CANDIDATES=0
export SKIP_CANDIDATES=0
```

Outputs:
- `results/<DATASET>/<RUN_NAME>/output.csv`
- `results/<DATASET>/<RUN_NAME>/result.txt`
- `honest_comparison_table.md`
- `honest_all_runs_table.md`

## Windows-only alternative
If you insist on PowerShell on Windows + conda, use:

```powershell
.\rerun_all_best_settings.ps1
```
