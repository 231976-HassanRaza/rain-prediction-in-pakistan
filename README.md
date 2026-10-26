# Rain Tomorrow Predictor — Islamabad & Karachi
ML model → Flask REST API → Angular form → GitHub Actions CI → GitHub Pages (static demo)

**Author:** Hassan Raza — Week 6 DevOps Lab
**GitHub repo:** https://github.com/YOUR_USERNAME/YOUR_REPO
**GitHub Pages (static UI only):** https://YOUR_USERNAME.github.io/YOUR_REPO/

## 1. Problem / task
Binary classification: will it rain **tomorrow** (>= 1 mm) in Islamabad or Karachi? Inputs are today's daily weather
(ERA5 reanalysis via Open-Meteo), lag features and rolling sums. Target: `rain_next_day`.

## 2. Model provenance
Trained by me in `notebooks/rain_in_pakistan_decision_trees_random_forests.ipynb` and re-built as one fitted sklearn
`Pipeline` by `backend/train_model.py` (imputer → MinMaxScaler → one-hot city → RandomForest). Preprocessing is fitted on
**train years only (2000–2018)**; validation 2019–2021; test 2022–2025. Tuned on validation ROC-AUC.
Saved bundle: `backend/models/model_bundle.joblib` (keys: pipeline, features, task, model_version, class_labels).
Test results are in `docs/metrics.json` and `docs/technical_report.md`.

## 3. Input schema (68 raw features)
`city` (Islamabad | Karachi) + 67 numeric weather/lag/rolling features. Exact names and order are stored in the bundle
(`features`), in `backend/test_payload.json`, and in `frontend/src/app/feature-schema.ts`.
The four "tomorrow" columns (`precip_next_day`, `rain_next_day`, `heavy_next_day`, `rain_class_next_day`) are
**never** inputs (data leakage).

## 4. Versions
Python 3.12, Node 22+ (LTS), npm 10+, Angular CLI 21, Flask 3.1, scikit-learn 1.8.0 (pinned in `backend/requirements.txt`).

## 5. Install
```powershell
cd D:\ml_project
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
cd frontend
npm install
cd ..
```
(Optional rebuild of the model: `python backend\train_model.py`)

## 6. Run locally (3 terminals)
Terminal 1 — Flask (keep open):
```powershell
cd D:\ml_project
.\.venv\Scripts\Activate.ps1
python backend\app.py
```
Terminal 2 — Angular (keep open):
```powershell
cd D:\ml_project\frontend
ng serve --open --proxy-config proxy.conf.json
```
Terminal 3 — tests and Git:
```powershell
cd D:\ml_project
python -m pytest -q backend\tests
python backend\test_api.py
curl.exe --noproxy "*" -i http://localhost:4200/api/health
```
Open http://localhost:4200, click **Load sample**, then **Run local prediction**.

## 7. API
- `GET /health` → `{status, features, task}`
- `POST /predict` (JSON with all 68 features) → `{prediction, label, rain_probability, probabilities, task, disclaimer}`
- 400 on missing/extra fields or invalid JSON.

## 8. Deployment limitations
GitHub Pages hosts **only the static Angular interface**. It cannot run Flask or the model, so on the public site the
prediction button is disabled and a notice is shown. Live predictions need Flask + Angular running locally.
Public predictions would need a separately hosted secure HTTPS backend.

## 9. CI/CD
- `.github/workflows/ci.yml`: backend pytest (all 5 tests) + Angular build + uploads `angular-build` artifact.
- `.github/workflows/pages.yml`: builds Angular with the correct base-href and deploys to GitHub Pages.

## 10. Ethics / research disclaimer
Teaching prototype only. Rain values are ERA5 reanalysis (modelled, not gauge measurements); only two cities are used.
**Not an official weather forecast** — do not use for safety-critical decisions.
