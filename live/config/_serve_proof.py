
import sys, json, time, threading, urllib.request
sys.path.insert(0, r"V:\A\Ai\COSMOS\cosmos")
from cosmos_kernel import Kernel
from cosmos_service import Service
k = Kernel(r"V:\A\Ai\COSMOS\live", worker="serve", read_only=False)
svc = Service(k, host="127.0.0.1", port=0)
svc.serve_background()
base = "http://127.0.0.1:%d" % svc.port
def g(p):
    req = urllib.request.Request(base + p)
    req.add_header("Authorization", "Bearer " + svc.token)
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode())
out = {"status_ready": g("/api/v1/status")["ready"],
       "health_verdict": g("/api/v1/health")["verdict"],
       "events_head": g("/api/v1/events?since_seq=0")["head_seq"]}
svc.shutdown()
print(json.dumps(out))
