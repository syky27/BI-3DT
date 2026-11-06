#!/usr/bin/env python3
"""rec.py PORT OUTDIR FPS -- capture ui.screenshot frames until OUTDIR/stop exists"""
import sys, time, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sc import control
port=int(sys.argv[1]); out=sys.argv[2]; fps=float(sys.argv[3]); os.makedirs(out, exist_ok=True)
i=0; t0=time.time(); lat=[]
while not os.path.exists(os.path.join(out,"stop")):
    t=time.time(); r=control(port,"ui.screenshot",{"path":os.path.join(out,f"f{i:05d}.png")}); lat.append(time.time()-t)
    i+=1
    d=t0+i/fps-time.time()
    if d>0: time.sleep(d)
print(json.dumps({"frames":i,"seconds":time.time()-t0,"avg_latency_ms":1000*sum(lat)/max(1,len(lat)),"max_ms":1000*max(lat)}))
