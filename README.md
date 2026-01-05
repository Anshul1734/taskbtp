# Cross-Cultural Modeling — AU Extraction & Analysis

This repository contains a reproducible pipeline to extract and analyze facial Action Units (AUs) for Happy vs Sad expressions using OpenFace outputs. It includes example data, analysis scripts, plotting, and a generated slide deck.

Recommended dataset: CK+ (Cohn-Kanade). Reason: labeled posed sequences with clear onset→apex frames, includes Happy and Sad labels, ideal for AU/time-series analysis. If you cannot access CK+, you can use JAFFE or another public dataset — adapt `scripts/run_featureextraction.ps1` accordingly.

Contents
- `scripts/run_featureextraction.ps1` — PowerShell example commands to run OpenFace `FeatureExtraction.exe`.
- `data/sample_openface_output.csv` — synthetic example OpenFace CSV for quick demo and verification.
- `analysis/analyze_aus.py` — analysis pipeline: preprocessing, statistics, plots, and slide generation.
- `requirements.txt` — Python dependencies for analysis and slide generation.
- `outputs/` — created when running the analysis; will contain plots and `presentation.pptx`.

Quick start (Windows)

1. Install Python dependencies (recommend a venv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Place OpenFace `FeatureExtraction.exe` somewhere and update `scripts/run_featureextraction.ps1` with its path.

3. CK+ specific notes: use `scripts/prepare_ckplus.py` to help build a sequence->emotion mapping (you may need to adapt to your local CK+ layout). Then run `scripts/process_ckplus.ps1` (update paths inside) to batch-run `FeatureExtraction.exe` over CK+ sequences. The CSV outputs can be provided as a directory to the analysis script.

4. If you have a dataset (e.g., CK+), run the feature extraction for image sequences or videos as shown in `scripts/run_featureextraction.ps1`.

4. To run the analysis on the provided synthetic sample (quick demo):

```powershell
python analysis\analyze_aus.py --input data/sample_openface_output.csv --out outputs
```

This will produce plots and `outputs/presentation.pptx` (10 slides, concise results).

Reproducibility notes
- The scripts are built to work with OpenFace CSV outputs (columns like `AU06_r`, `AU12_r`, `AU01_r`, `AU04_r`, `AU15_r`). If your CSV uses different column names, update `analysis/analyze_aus.py` accordingly.

License & data
- This repo does not include real dataset images or videos. Download CK+ or your chosen dataset and run OpenFace locally to produce CSV inputs.
