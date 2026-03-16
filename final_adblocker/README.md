# Final Adblocker Demo

Jupyter-friendly version of the adblocker Random Forest training pipeline. Everything lives in this folder so you can demo without touching the rest of the repo.

## Setup

```powershell
cd C:\Users\DELL\email-digest\final_adblocker
python -m pip install -r requirements.txt
```

## Run the notebook

```powershell
cd C:\Users\DELL\email-digest\final_adblocker
jupyter notebook --no-browser
```

Then open `adblocker_demo.ipynb`, run all cells, and you will get:
- `cross_validation_report.csv`
- `original_dataset.joblib`
- inline plots for CV scores, confusion matrix, and feature importance.

## Notes
- The notebook reads `ad.data` in this folder; no other paths are required.
- `main.py` is also copied here if you prefer running the original script.

