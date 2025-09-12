# worker/train_ae_pytorch.py
import os, json, joblib
import pandas as pd, numpy as np
import torch, torch.nn as nn
from sklearn.preprocessing import StandardScaler

FEATURE_CSV = "worker/features.csv"
OUT_DIR = "models"
NUM_FEATURES = ["hour_of_day","day_of_week","delta_minutes","geodistance_km","device_change","failed_prev_5"]
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(FEATURE_CSV)
train_df = df[df['label']==0].copy()
X = train_df[NUM_FEATURES].values.astype(float)

scaler_path = os.path.join(OUT_DIR, "scaler.pkl")
if os.path.exists(scaler_path):
    scaler = joblib.load(scaler_path)
else:
    scaler = StandardScaler().fit(X); joblib.dump(scaler, scaler_path)
Xs = scaler.transform(X)
Xt = torch.tensor(Xs, dtype=torch.float32)

class AE(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(dim, max(4,dim//2)), nn.ReLU(), nn.Linear(max(4,dim//2), max(2,dim//3)), nn.ReLU())
        self.dec = nn.Sequential(nn.Linear(max(2,dim//3), max(4,dim//2)), nn.ReLU(), nn.Linear(max(4,dim//2), dim))
    def forward(self,x): return self.dec(self.enc(x))

dim = Xt.shape[1]
model = AE(dim)
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

epochs=60; batch=128
loader = torch.utils.data.DataLoader(torch.utils.data.TensorDataset(Xt), batch_size=batch, shuffle=True)
for e in range(epochs):
    model.train(); epoch_loss=0.0
    for (b,) in loader:
        opt.zero_grad(); out = model(b)
        loss = loss_fn(out,b); loss.backward(); opt.step()
        epoch_loss += float(loss)*b.size(0)
    epoch_loss /= len(loader.dataset)
    if e%10==0: print(f"Epoch {e}/{epochs} loss={epoch_loss:.6f}")

model.eval()
with torch.no_grad():
    rec = model(Xt)
    rec_err = ((rec - Xt)**2).mean(dim=1).numpy()

ae_mean = float(rec_err.mean()); ae_std = float(rec_err.std())
torch.save(model.state_dict(), os.path.join(OUT_DIR,"autoencoder.pth"))
with open(os.path.join(OUT_DIR,"ae_stats.json"), "w") as f:
    json.dump({"ae_mean":ae_mean, "ae_std":ae_std, "features": NUM_FEATURES}, f)
print("Saved AE model & stats to", OUT_DIR, "ae_mean,ae_std:", ae_mean, ae_std)
