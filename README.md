# Industrial Health Agent

An educational industrial predictive-maintenance agent built with Python and the NASA C-MAPSS FD001 turbofan benchmark.

## What it does

The project combines a remaining-useful-life (RUL) prediction model with sensor-trend rules and a local maintenance knowledge base.

```text
Sensor trajectories
    -> RUL prediction
    -> Risk thresholding
    -> Sensor trend checks
    -> Maintenance knowledge retrieval
    -> Markdown diagnostic report
```

## Project structure

- `src/`: data preparation, modeling, evaluation, retrieval, and agent orchestration
- `tests/`: automated tests
- `docs/`: plots and maintenance knowledge
- `data/raw/`: local dataset files, excluded from Git
- `artifacts/`: generated predictions and reports, excluded from Git

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install numpy pandas matplotlib scikit-learn pytest
```

Place the three FD001 files in `data/raw/`:

- `train_FD001.txt`
- `test_FD001.txt`
- `RUL_FD001.txt`

## Run

```powershell
python src\prepare_data.py
python src\save_predictions.py
python src\agent_cli.py --unit 18
python -m pytest -q
```

The generated report is written to `artifacts/diagnostic_report_unit_18.md`.

## Current benchmark results

The current Random Forest baseline on the official FD001 test set achieved:

- MAE: 20.89 cycles
- RMSE: 29.24 cycles
- Risk threshold calibrated on validation data: 20 cycles
- Official test risk result: 14 true positives, 2 false negatives, 0 false positives, and 84 true negatives

These values are for research and learning only. C-MAPSS is simulated data, and the model is not a certified maintenance or aviation-safety system.

## Limitations and next steps

- The current agent uses deterministic local tools rather than an external LLM.
- The knowledge retrieval component is keyword-based rather than embedding-based.
- The model can overestimate remaining life for some engines.
- Future work includes uncertainty estimation, stronger validation, semantic retrieval, and an LLM interface with human approval safeguards.
