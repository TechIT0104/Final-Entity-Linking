param(
  [string]$BelaEnvName = "bela39",
  [string]$LlmEnvName = "llm",
  [string]$Device = "cuda:0",
  [int]$TopK = 50,
  [int]$BatchSize = 4,
  [switch]$ForceCandidates,
  [switch]$SkipCandidates
)

$ErrorActionPreference = "Stop"

function Ensure-Conda {
  if (-not (Get-Command conda -ErrorAction SilentlyContinue)) {
    throw "conda not found in PATH. Install Miniconda/Anaconda or run this on a machine with conda." 
  }
  # Initialize conda for PowerShell session
  & conda "shell.powershell" "hook" | Out-String | Invoke-Expression
}

function Invoke-Step([string]$Title, [scriptblock]$Block) {
  Write-Host "\n=== $Title ===" -ForegroundColor Cyan
  & $Block
}

# Paper best settings (as per README table) mapped to exact run folder names already used in results/.
# Dataset folder names are under test_data/ and results/.
$Runs = @(
  @{ Dataset = "HIPE_DE"; Lang = "de"; Script = "filter_and_prompt_chain.py"; NCandidates = 30; Threshold = 21.4;  ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_chain_median_k30_de" },
  @{ Dataset = "HIPE_EN"; Lang = "en"; Script = "filter_and_prompt_chain.py"; NCandidates = 20; Threshold = $null; ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_chain_k20_en" },
  @{ Dataset = "HIPE_FR"; Lang = "fr"; Script = "filter_and_prompt.py";       NCandidates = 20; Threshold = $null; ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_van_k20_fr" },

  @{ Dataset = "NEWSEYE_DE"; Lang = "de"; Script = "filter_and_prompt_chain.py"; NCandidates = 30; Threshold = 25.0;  ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_chain_k30_de" },
  @{ Dataset = "NEWSEYE_FI"; Lang = "fi"; Script = "filter_and_prompt_chain.py"; NCandidates = 20; Threshold = $null; ModelId = "LumiOpen/Llama-Poro-2-8B-Instruct";          RunName = "poro2_8B_chain_k20_fi" },
  @{ Dataset = "NEWSEYE_FR"; Lang = "fr"; Script = "filter_and_prompt_chain.py"; NCandidates = 20; Threshold = 21.35; ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_chain_median_k20_fr" },
  @{ Dataset = "NEWSEYE_SV"; Lang = "sv"; Script = "filter_and_prompt_chain.py"; NCandidates = 20; Threshold = 25.0;  ModelId = "google/gemma-3-27b-it";                     RunName = "gemma_27B_chain_median_k20_sv" },

  @{ Dataset = "AJMC_DE"; Lang = "de"; Script = "filter_and_prompt.py";       NCandidates = 50; Threshold = 21.5;  ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_van_k50_de" },
  @{ Dataset = "AJMC_EN"; Lang = "en"; Script = "filter_and_prompt.py";       NCandidates = 50; Threshold = $null; ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_van_k50_en" },
  @{ Dataset = "AJMC_FR"; Lang = "fr"; Script = "filter_and_prompt.py";       NCandidates = 20; Threshold = $null; ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_van_k20_fr" },

  @{ Dataset = "MHERCL_EN"; Lang = "en"; Script = "filter_and_prompt_chain.py"; NCandidates = 20; Threshold = $null; ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_chain_k20_en" },
  @{ Dataset = "MHERCL_IT"; Lang = "it"; Script = "filter_and_prompt_chain.py"; NCandidates = 20; Threshold = $null; ModelId = "mistralai/Mistral-Small-24B-Instruct-2501"; RunName = "mistral_24B_chain_k20_it" }
)

Ensure-Conda

Invoke-Step "Workspace" {
  Write-Host "PWD: $PWD"
  if (-not (Test-Path .\test_data)) { throw "Missing test_data/" }
  if (-not (Test-Path .\results)) { New-Item -ItemType Directory .\results | Out-Null }
}

if (-not $SkipCandidates) {
  Invoke-Step "Candidate retrieval (BELA)" {
    conda activate $BelaEnvName
    foreach ($r in $Runs) {
      $dataset = $r.Dataset
      $lang = $r.Lang
      $datasetPath = Join-Path .\test_data $dataset
      if ($dataset -eq "MHERCL_IT") {
        # test_data uses MHERCL_it (lowercase i)
        $datasetPath = Join-Path .\test_data "MHERCL_it"
      }
      $outDir = Join-Path .\results $dataset
      if (-not (Test-Path $outDir)) { New-Item -ItemType Directory $outDir | Out-Null }

      $candPath = Join-Path $outDir ("candidates_test_top{0}_{1}.json" -f $TopK, $lang)
      if ((-not (Test-Path $candPath)) -or $ForceCandidates) {
        Write-Host "Retrieving candidates for $dataset ($lang) -> $candPath" -ForegroundColor Yellow
        python .\get_candidates.py --dataset_path $datasetPath --output_dir $outDir --top_k $TopK --lang $lang --batch_size $BatchSize --device $Device
      } else {
        Write-Host "Candidates exist for $dataset ($lang); skipping (use -ForceCandidates to rerun)." -ForegroundColor DarkGray
      }
    }
  }
}

Invoke-Step "LLM prompting + evaluation" {
  conda activate $LlmEnvName

  foreach ($r in $Runs) {
    $dataset = $r.Dataset
    $lang = $r.Lang
    $script = $r.Script
    $nCandidates = $r.NCandidates
    $threshold = $r.Threshold
    $modelId = $r.ModelId
    $runName = $r.RunName

    $datasetPath = Join-Path .\test_data $dataset
    if ($dataset -eq "MHERCL_IT") {
      $datasetPath = Join-Path .\test_data "MHERCL_it"
    }

    $datasetResultsDir = Join-Path .\results $dataset
    $candPath = Join-Path $datasetResultsDir ("candidates_test_top{0}_{1}.json" -f $TopK, $lang)
    if (-not (Test-Path $candPath)) {
      throw "Missing candidates file: $candPath. Run without -SkipCandidates first." 
    }

    $runDir = Join-Path $datasetResultsDir $runName
    if (-not (Test-Path $runDir)) { New-Item -ItemType Directory $runDir | Out-Null }

    Write-Host "Running $dataset/$runName using $script" -ForegroundColor Yellow

    $args = @(
      ".\\$script",
      "--json_f", $candPath,
      "--dataset_path", $datasetPath,
      "--output_dir", $runDir,
      "--n_candidates", $nCandidates,
      "--model_id", $modelId
    )
    if ($null -ne $threshold) {
      $args += @("--threshold", $threshold)
    }

    python @args

    Write-Host "Evaluating $dataset/$runName" -ForegroundColor Yellow
    python .\eval.py --path_data $datasetPath --path_results $runDir
  }
}

Invoke-Step "Honest comparison tables" {
  python .\honest_eval_report.py
  Write-Host "See honest_comparison_table.md and honest_all_runs_table.md" -ForegroundColor Green
}

Write-Host "\nDONE." -ForegroundColor Green
