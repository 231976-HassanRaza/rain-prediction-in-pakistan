# Technical Report — Rain Tomorrow Predictor (ML → Flask → Angular → GitHub CI/CD)
Author: Hassan Raza

## 1. Objective
Predict whether it will rain tomorrow (>= 1 mm) in Islamabad and Karachi from today's weather, then package the
trained model as a Flask REST API with an Angular front end, and automate checks and deployment with GitHub Actions.

## 2. Data
`data/model_ready.csv`: 18,934 city-days (2 cities x 9,467 days, 2000-01-30 to 2025-12-30), 73 columns. Source: ERA5 daily data via
Open-Meteo (built by our `build_dataset.py`). `data/raw_daily.csv` holds the 36 raw daily variables.
68 columns are model inputs (city + 67 numeric incl. lags, 3/7/14/30-day rolling rain, pressure change, days since rain).
Four columns describing tomorrow are excluded as leakage.

## 3. Model
Random Forest inside one sklearn Pipeline: mean imputer -> MinMaxScaler -> one-hot(city) -> RandomForestClassifier.
Fitted on 2000-2018 only (13822 rows); validation 2019-2021 (2192); test 2022-2025 (2920).
Hyper-parameters chosen by validation ROC-AUC: {'n_estimators': 200, 'max_depth': 20}. Depth was capped so the model file is only ~6 MB.

## 4. Test-set results (2022-2025)
| Metric | Value |
|---|---|
| Accuracy | 0.870 |
| Precision | 0.706 |
| Recall | 0.488 |
| F1 | 0.577 |
| ROC-AUC | 0.908 |
| Baseline accuracy (always "No rain") | 0.818 |

Rain is rare (~18% of days), so accuracy alone is misleading; the model beats the always-"No rain" baseline but recall at
the default 0.5 threshold is modest (~49%). The notebook (section 13) shows class weighting and validation-tuned thresholds
improve recall.

## 5. Architecture
Browser (Angular, localhost:4200) -> `POST /api/predict` -> Angular dev proxy -> Flask `POST /predict` (127.0.0.1:5000)
-> schema validation -> fitted pipeline -> JSON. GitHub Actions runs pytest + Angular build; GitHub Pages hosts the static UI only.

## 6. Testing
- `backend/test_pipeline.py`: direct inference on the sample record (prediction 1, P(rain) = 0.805).
- `backend/tests/test_api.py`: health, valid prediction, missing feature (400), invalid JSON (400).
- `backend/tests/test_structure.py`: required files exist.
- CI runs all 5 tests on Ubuntu / Python 3.12.

## 7. Limitations and ethics
ERA5 is modelled reanalysis, not rain-gauge data; two cities only; the front end needs all 68 inputs, so lag/rolling
features must be taken from the dataset (sample buttons provided). Static GitHub Pages cannot run predictions. Research
prototype, not an official forecast.

## 8. Conclusion
The lab pipeline (train -> package -> API -> UI -> Git -> CI -> Pages) works end to end with a real model.
