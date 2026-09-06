# MHEL-LLAMO Server Setup Complete ✓

## Server Connection Details
- **Host**: 172.20.70.170
- **Username**: kmpooja
- **Project Location**: ~/MHEL-LLAMO

## Environments Created

### 1. BELA39 Environment (Bi-encoder Model)
- **Location**: `/home/kmpooja/miniconda3/envs/bela39`
- **Python**: 3.10
- **GPU Support**: CUDA 11.8 with PyTorch 2.6.0
- **Key Packages**:
  - torch==2.6.0+cu118
  - transformers==5.6.2
  - sentence-transformers==5.4.1
  - pytorch-lightning==2.6.1
  - faiss-cpu
  - datasets

### 2. LLM Environment (Large Language Models)
- **Location**: `/home/kmpooja/miniconda3/envs/llm`
- **Python**: 3.10
- **GPU Support**: CUDA 11.8 with PyTorch 2.6.0
- **Key Packages**:
  - torch==2.6.0+cu118
  - transformers==5.6.2
  - accelerate==1.13.0
  - bitsandbytes==0.42.0

## Running the Model

### Step 1: Candidate Retrieval with BELA (Bi-encoder)
```bash
# SSH into server
ssh kmpooja@172.20.70.170

# Navigate to project
cd ~/MHEL-LLAMO

# Activate bela39 environment
conda activate bela39

# Run candidate retrieval (example for HIPE_EN dataset)
python get_candidates.py \
  --dataset_path ./test_data/HIPE_EN \
  --output_dir ./results/HIPE_EN \
  --top_k 50 \
  --lang en
```

### Step 2: NIL Prediction & Candidate Selection with LLM
```bash
# Activate llm environment
conda activate llm

# Run LLM-based filtering and candidate selection
python filter_and_prompt_chain.py \
  --json_f results/HIPE_EN/candidates_test_top50_en.json \
  --dataset_path ./test_data/HIPE_EN \
  --output_dir ./results/HIPE_EN \
  --threshold 21.24 \
  --n_candidates 20 \
  --model_id mistralai/Mistral-Small-24B-Instruct-2501

# If the model repo is gated, authenticate once (preferred):
#   huggingface-cli login
# or set an env var (preferred over --hf_token):
#   export HUGGINGFACE_HUB_TOKEN=...
```

### Step 3: Evaluate Results
```bash
conda activate llm

python eval.py \
  --path_data ./test_data/HIPE_EN \
  --path_results ./results/HIPE_EN
```

## Available Test Datasets
The following benchmarks are available in `./test_data/`:
- HIPE_EN, HIPE_DE, HIPE_FR
- AJMC_EN, AJMC_DE, AJMC_FR
- MHERCL_EN, MHERCL_it
- NEWSEYE_DE, NEWSEYE_FI, NEWSEYE_FR, NEWSEYE_SV

## Recommended Models (from paper)
| Dataset | Language | Model | N. Candidates | Threshold |
|---------|----------|-------|---------------|-----------|
| HIPE-2020 | en | mistralai/Mistral-Small-24B-Instruct-2501 | 20 | - |
| HIPE-2020 | de | mistralai/Mistral-Small-24B-Instruct-2501 | 30 | 21.4 |
| HIPE-2020 | fr | mistralai/Mistral-Small-24B-Instruct-2501 | 20 | - |
| NewsEye | de | mistralai/Mistral-Small-24B-Instruct-2501 | 30 | 25 |
| NewsEye | fi | LumiOpen/Llama-Poro-2-8B-Instruct | 20 | - |
| NewsEye | fr | mistralai/Mistral-Small-24B-Instruct-2501 | 20 | 21.35 |
| NewsEye | sv | google/gemma-3-27b-it | 20 | 25 |

## Quick Commands

### Check environment
```bash
# Verify bela39
/home/kmpooja/miniconda3/envs/bela39/bin/python --version

# Verify llm
/home/kmpooja/miniconda3/envs/llm/bin/python --version
```

### View project structure
```bash
cd ~/MHEL-LLAMO
ls -la
```

### Check available results
```bash
ls -la ~/MHEL-LLAMO/results/
```

## Notes
- Both environments use CUDA 11.8 for GPU acceleration
- For low-resource settings, consider:
  - `mistralai/Ministral-8B-Instruct-2410` for EN/FR/DE
  - `google/gemma-3-12b-it` for Swedish
- Make sure to have a HuggingFace token for gated models
- GPU memory requirement: ~24GB for Mistral-24B models

## Troubleshooting

If you encounter any issues:
1. Verify conda environments: `conda env list`
2. Check Python version in each env: `conda activate bela39 && python --version`
3. Verify GPU access: `python -c "import torch; print(torch.cuda.is_available())"`
4. Check available disk space: `df -h`

## Next Steps
1. Choose your test dataset and language
2. Run candidate retrieval with BELA
3. Run LLM-based filtering (ensure you have HuggingFace token if using gated models)
4. Evaluate results with eval.py

For more details, see README.md in the project directory.
