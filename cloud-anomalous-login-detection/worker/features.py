# worker/features.py
import pandas as pd, math, os
from datetime import datetime

SRC = "../data/synthetic_logins.csv"
OUT = "worker/features.csv"

def haversine(a,b):
    lat1, lon1 = a; lat2, lon2 = b
    R=6371.0
    phi1,phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1); dlambda = math.radians(lon2-lon1)
    x = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.asin(math.sqrt(x))

def build():
    df = pd.read_csv(SRC)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values(['user_id','timestamp']).reset_index(drop=True)
    out=[]
    last={}
    for _, r in df.iterrows():
        user = r['user_id']; ts = r['timestamp']; lat=float(r['lat']); lon=float(r['lon'])
        if user in last:
            prev = last[user]
            delta_min = (ts - prev['timestamp']).total_seconds()/60.0
            dist = haversine((prev['lat'],prev['lon']),(lat,lon))
            device_change = 1 if r['device_hash'] != prev['device_hash'] else 0
        else:
            delta_min = 99999.0; dist = 0.0; device_change = 0
        prev_rows = df[(df['user_id']==user) & (df['timestamp'] < ts)].tail(5)
        failed_prev_5 = int((prev_rows['success']==0).sum())
        out.append({
            "user_id": user,
            "timestamp": ts.isoformat(),
            "hour_of_day": ts.hour,
            "day_of_week": ts.weekday(),
            "delta_minutes": delta_min,
            "geodistance_km": dist,
            "device_change": device_change,
            "failed_prev_5": failed_prev_5,
            "label": int(r.get("label",0))
        })
        last[user] = {"timestamp": ts, "lat": lat, "lon": lon, "device_hash": r['device_hash']}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    pd.DataFrame(out).to_csv(OUT, index=False)
    print("Wrote", OUT, "rows:", len(out))

if __name__=="__main__":
    build()
