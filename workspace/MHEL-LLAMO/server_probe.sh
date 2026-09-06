#!/usr/bin/env bash
set -euo pipefail

echo "=== OS ==="
uname -a || true
if [[ -f /etc/os-release ]]; then
  cat /etc/os-release
fi

echo "\n=== GPU ==="
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi || echo "nvidia-smi not found"

echo "\n=== CUDA libs (ldconfig) ==="
command -v ldconfig >/dev/null 2>&1 && ldconfig -p | grep -E "libcuda|libcudart" || true

echo "\n=== Disk / RAM ==="
df -h . || true
free -h || true

echo "\n=== Conda ==="
if command -v conda >/dev/null 2>&1; then
  conda --version
  conda info -a | sed -n '1,120p'
else
  echo "conda not found"
fi

echo "\n=== Python ==="
command -v python >/dev/null 2>&1 && python -V || echo "python not found"

echo "\n=== Torch / Transformers / FAISS (in current env) ==="
python - <<'PY'
import sys
print('python', sys.version)

def try_import(name):
    try:
        mod = __import__(name)
        print(name, 'OK', getattr(mod, '__version__', ''))
        return mod
    except Exception as e:
        print(name, 'FAIL', repr(e))
        return None

torch = try_import('torch')
try_import('transformers')
faiss = try_import('faiss')

if torch is not None:
    print('cuda_available', torch.cuda.is_available())
    print('cuda_device_count', torch.cuda.device_count())
    if torch.cuda.is_available():
        print('cuda_device_name_0', torch.cuda.get_device_name(0))
PY

echo "\n=== pip freeze (first 60 lines) ==="
command -v pip >/dev/null 2>&1 && pip freeze | sed -n '1,60p' || echo "pip not found"
