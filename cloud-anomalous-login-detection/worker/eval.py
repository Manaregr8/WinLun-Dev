# worker/eval.py
import pandas as pd
from ensemble import score_features, combine
import matplotlib.pyplot as plt
import os

df = pd.read_csv("worker/features.csv")
NUM_FEATURES = ["hour_of_day","day_of_week","delta_minutes","geodistance_km","device_change","failed_prev_5"]

rows=[]
for _, r in df.iterrows():
    feats=[r[c] for c in NUM_FEATURES]
    scored = score_features(feats)
    # simple rule: impossible travel
    rule = 100 if (r['geodistance_km']>500 and r['delta_minutes']<180) else 0
    risk = combine(rule, scored['if_norm'], scored['ae_norm'])
    rows.append({"label": int(r['label']), "risk": risk})
ev = pd.DataFrame(rows)
print(ev.groupby('label')['risk'].describe())

plt.figure(figsize=(6,4))
ev[ev['label']==0]['risk'].hist(bins=50, alpha=0.6, label='normal')
ev[ev['label']==1]['risk'].hist(bins=50, alpha=0.6, label='anomaly')
plt.legend(); plt.xlabel('risk'); plt.ylabel('count')
plt.tight_layout()
os.makedirs("reports", exist_ok=True)
plt.savefig("reports/risk_dist.png")
print("Saved reports/risk_dist.png")
