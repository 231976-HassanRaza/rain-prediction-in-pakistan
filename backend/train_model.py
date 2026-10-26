"""Re-creates the notebook's Random Forest as ONE fitted sklearn Pipeline
(imputer -> MinMax scaler -> one-hot city -> RandomForest) and saves
backend/models/model_bundle.joblib  (Stage 4 of the lab manual).

Run from project root:   python backend\train_model.py
Preprocessing is fitted on the TRAIN years only (2000-2018), like the notebook.
"""
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder

ROOT = Path(__file__).resolve().parent.parent
RANDOM_STATE = 42
LEAK_COLS = ["precip_next_day", "rain_next_day", "heavy_next_day", "rain_class_next_day"]
TARGET = "rain_next_day"

df = pd.read_csv(ROOT / "data" / "model_ready.csv", parse_dates=["date"])
df = df.dropna(subset=[TARGET]).sort_values(["city", "date"]).reset_index(drop=True)

input_cols = [c for c in df.columns if c not in ["date"] + LEAK_COLS]
year = df["date"].dt.year
train, val, test = df[year < 2019], df[(year >= 2019) & (year <= 2021)], df[year >= 2022]

numeric_cols = train[input_cols].select_dtypes(include=np.number).columns.tolist()
categorical_cols = train[input_cols].select_dtypes(exclude=np.number).columns.tolist()
print("numeric:", len(numeric_cols), "categorical:", categorical_cols)


def make_pipeline(**rf_params):
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="mean")),
                          ("sc", MinMaxScaler())]), numeric_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_cols),
    ])
    rf = RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1, **rf_params)
    return Pipeline([("preprocess", pre), ("model", rf)])


Xtr, ytr = train[input_cols], train[TARGET].astype(int)
Xva, yva = val[input_cols], val[TARGET].astype(int)
Xte, yte = test[input_cols], test[TARGET].astype(int)

# Same grid idea as the notebook (depth capped so the model file stays small enough for GitHub)
grid = [{"n_estimators": 100, "max_depth": 15},
        {"n_estimators": 200, "max_depth": 15},
        {"n_estimators": 200, "max_depth": 20}]
best, best_auc = None, -1
for params in grid:
    p = make_pipeline(**params).fit(Xtr, ytr)
    auc = roc_auc_score(yva, p.predict_proba(Xva)[:, 1])
    print(params, "val AUC = %.4f" % auc)
    if auc > best_auc:
        best, best_auc, best_params = p, auc, params
print("Best params:", best_params)

pred = best.predict(Xte)
prob = best.predict_proba(Xte)[:, 1]
metrics = {
    "best_params": best_params,
    "test_accuracy": accuracy_score(yte, pred),
    "test_precision": precision_score(yte, pred, zero_division=0),
    "test_recall": recall_score(yte, pred, zero_division=0),
    "test_f1": f1_score(yte, pred, zero_division=0),
    "test_roc_auc": roc_auc_score(yte, prob),
    "baseline_always_no_rain_accuracy": 1 - yte.mean(),
    "rows": {"train": len(train), "val": len(val), "test": len(test)},
}
print(json.dumps(metrics, indent=2, default=float))

bundle = {
    "pipeline": best,
    "features": input_cols,          # EXACT training input order (city + numeric)
    "task": "classification",
    "model_version": "1.0",
    "class_labels": {"0": "No rain tomorrow", "1": "Rain tomorrow"},
}
out = ROOT / "backend" / "models" / "model_bundle.joblib"
out.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(bundle, out, compress=3)
print("Saved", out, "size MB = %.1f" % (out.stat().st_size / 1e6), "| features:", len(input_cols))

(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "metrics.json").write_text(json.dumps(metrics, indent=2, default=float), encoding="utf-8")

# Sample rows for the API tests and the Angular "load sample" buttons (non-sensitive weather data)
# pick clear, correctly-predicted examples so the demo is easy to explain
test = test.assign(_p=prob)
rainy = test[(test.city == "Islamabad") & (test[TARGET] == 1) & (test._p > 0.8)].iloc[0]
dry = test[(test.city == "Karachi") & (test[TARGET] == 0) & (test._p < 0.05)].iloc[100]
print("Sample dates:", rainy["date"].date(), rainy["city"], "| ", dry["date"].date(), dry["city"])
samples = pd.DataFrame([rainy[input_cols], dry[input_cols]])
samples.to_csv(ROOT / "data" / "sample_inputs.csv", index=False)
print("Wrote data/sample_inputs.csv (row 1 = Islamabad rainy-next-day, row 2 = Karachi dry-next-day)")

# Angular feature schema (min/max from the training data)
FIELD_DOC = {}
schema = []
for c in input_cols:
    if c in categorical_cols:
        opts = sorted(train[c].dropna().unique().tolist())
        schema.append({"name": c, "label": c.replace("_", " ").title(), "kind": "category",
                       "required": True, "options": opts})
    else:
        lo, hi = float(df[c].min()), float(df[c].max())
        pad = 0.05 * (hi - lo)
        schema.append({"name": c, "label": c, "kind": "number", "required": True,
                       "min": round(lo - pad, 4), "max": round(hi + pad, 4)})
(ROOT / "backend" / "feature_schema.json").write_text(json.dumps(
    {"features": schema,
     "samples": [{"title": "Islamabad (rain followed)", "values": json.loads(samples.iloc[[0]].to_json(orient="records"))[0]},
                 {"title": "Karachi (dry followed)", "values": json.loads(samples.iloc[[1]].to_json(orient="records"))[0]}]},
    indent=1), encoding="utf-8")
print("Wrote backend/feature_schema.json")
