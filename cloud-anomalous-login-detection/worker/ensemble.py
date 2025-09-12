# worker/ensemble.py
import os, joblib, json, math, numpy as np, torch
from sklearn.preprocessing import StandardScaler

MODELS_DIR = "models"
NUM_FEATURES = ["hour_of_day","day_of_week","delta_minutes","geodistance_km","device_change","failed_prev_5"]

scaler = joblib.load(os.path.join(MODELS_DIR,"scaler.pkl"))
if_model = joblib.load(os.path.join(MODELS_DIR,"isolation_forest.joblib"))
with open(os.path.join(MODELS_DIR,"if_stats.json")) as f: if_stats = json.load(f)
with open(os.path.join(MODELS_DIR,"ae_stats.json")) as f: ae_stats = json.load(f)

# load AE structure then state
class AE(torch.nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.enc = torch.nn.Sequential(torch.nn.Linear(dim, max(4,dim//2)), torch.nn.ReLU(), torch.nn.Linear(max(4,dim//2), max(2,dim//3)), torch.nn.ReLU())
        self.dec = torch.nn.Sequential(torch.nn.Linear(max(2,dim//3), max(4,dim//2)), torch.nn.ReLU(), torch.nn.Linear(max(4,dim//2), dim))
    def forward(self,x): return self.dec(self.enc(x))

dim = len(NUM_FEATURES)
ae = AE(dim)
ae.load_state_dict(torch.load(os.path.join(MODELS_DIR,"autoencoder.pth"), map_location="cpu"))
ae.eval()

def logistic(z): return 1.0/(1.0+math.exp(-z))
def normalize_if(raw):
    mean = if_stats.get("if_mean",0.0); std = if_stats.get("if_std",1.0)
    z = (raw - mean) / (std + 1e-9)
    return logistic(z)
def normalize_ae(err):
    mean = ae_stats.get("ae_mean",0.0); std = ae_stats.get("ae_std",1.0)
    z = (err - mean) / (std + 1e-9)
    return logistic(z)

def score_features(feature_vector):
    X = np.array(feature_vector, dtype=float).reshape(1,-1)
    Xs = scaler.transform(X)
    raw_if = -if_model.score_samples(Xs)[0]   # higher -> more anomalous
    if_norm = normalize_if(raw_if)
    Xt = torch.tensor(Xs, dtype=torch.float32)
    with torch.no_grad():
        rec = ae(Xt).numpy()
    rec_err = float(((Xs - rec)**2).mean())
    ae_norm = normalize_ae(rec_err)
    return {"if_raw": raw_if, "if_norm": if_norm, "ae_err": rec_err, "ae_norm": ae_norm}

def combine(rule_score_0_100, if_norm, ae_norm, w_rule=0.5, w_if=0.3, w_ae=0.2):
    r = rule_score_0_100 / 100.0
    combined = w_rule*r + w_if*if_norm + w_ae*ae_norm
    return float(combined * 100.0)   # final 0..100
