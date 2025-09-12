# worker/train_if.py
import os, json, joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

FEATURE_CSV = "worker/features.csv"
OUT_DIR = "models"
NUM_FEATURES = ["hour_of_day","day_of_week","delta_minutes","geodistance_km","device_change","failed_prev_5"]

os.makedirs(OUT_DIR, exist_ok=True)
df = pd.read_csv(FEATURE_CSV)
train_df = df[df['label']==0].copy()
X = train_df[NUM_FEATURES].values

scaler = StandardScaler().fit(X)
Xs = scaler.transform(X)

clf = IsolationForest(n_estimators=200, contamination=0.01, random_state=42)
clf.fit(Xs)

train_scores = -clf.score_samples(Xs)    # higher -> more anomalous
if_mean = float(train_scores.mean()); if_std = float(train_scores.std())

joblib.dump(clf, os.path.join(OUT_DIR,"isolation_forest.joblib"))
joblib.dump(scaler, os.path.join(OUT_DIR,"scaler.pkl"))
with open(os.path.join(OUT_DIR,"if_stats.json"), "w") as f:
    json.dump({"if_mean": if_mean, "if_std": if_std, "features": NUM_FEATURES}, f)
print("Saved IF model to", OUT_DIR, "mean,std:", if_mean, if_std)
