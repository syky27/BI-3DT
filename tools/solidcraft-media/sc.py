#!/usr/bin/env python3
"""Tiny control-channel client for SolidCraft: sc.py PORT METHOD [JSON]"""
import json, socket, sys, os
from pathlib import Path
def token(port):
    t=os.environ.get("SOLIDCRAFT_CONTROL_TOKEN")
    if t: return t.strip()
    return (Path.home()/"Library/Application Support/SolidCraft/control"/f"{port}.token").read_text().strip()
def control(port, method, params=None):
    with socket.create_connection(("127.0.0.1", port), timeout=float(os.environ.get("SC_TIMEOUT","120"))) as s:
        s.sendall((json.dumps({"id":1,"method":method,"params":params or {},"token":token(port)})+"\n").encode())
        buf=b""
        while not buf.endswith(b"\n"):
            ch=s.recv(1<<16)
            if not ch: break
            buf+=ch
    return json.loads(buf or b"{}")
if __name__=="__main__":
    port=int(sys.argv[1]); m=sys.argv[2]; p=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
    r=control(port,m,p); print(json.dumps(r)[:3000])
