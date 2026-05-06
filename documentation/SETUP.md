# Setup Guide - Entity Linking Project

## Prerequisites

- Python 3.10+
- CUDA 12.0+ (for GPU support)
- pip or conda

## 1. Environment Setup

### Option A: Using Conda (Recommended)

```bash
# Create environment
conda create -n entity-linking python=3.11
conda activate entity-linking

# Install PyTorch with CUDA support
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia

# Install other dependencies
pip install transformers xgboost pandas tqdm scikit-learn
```

### Option B: Using pip with Virtual Environment

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install torch transformers xgboost pandas tqdm scikit-learn
```

## 2. Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import xgboost; print(f'XGBoost: {xgboost.__version__}')"
```

## 3. Optional: Download Pretrained Models

The scripts use pretrained models that will be downloaded automatically on first run:
- `microsoft/bela` - Bi-encoder model
- `mistralai/Mistral-24B` or `mistralai/Mistral-8B` - LLM models
- `cross-encoder/ms-marco-MiniLM-L-6-v2` - Cross-encoder for reranking

**Note:** First run may take time due to model downloads (several GB).

## 4. Prepare Data

Create the following directory structure:
```
dataset/
├── AJMC_EN/
│   ├── candidates_test_top50_en.json
│   ├── paragraphs_test.csv
│   └── entities_en.txt
├── MEWSLI-9/
│   └── [benchmark files]
└── README_DATASETS.md
```

See `documentation/DATASETS.md` for dataset details.

## 5. Troubleshooting

### CUDA Out of Memory
- Reduce batch size in scripts (default: 8)
- Enable mixed precision: `--mixed_precision`
- Use gradient accumulation: `--gradient_accumulation_steps=2`

### Model Not Found
- Check internet connection
- Set HuggingFace cache: `HF_HOME=/path/to/cache`
- Pre-download model: `python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/bela')"`

### Installation Issues
- Update pip: `pip install --upgrade pip`
- Clear cache: `pip cache purge`
- Use specific versions: `pip install transformers==4.30.0`

## 6. Next Steps

After setup, proceed to `documentation/USAGE.md` for running the pipelines.
