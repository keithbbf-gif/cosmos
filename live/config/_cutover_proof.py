
import sys, json
sys.path.insert(0, r"V:\A\Ai\COSMOS\cosmos")
from cosmos_kernel import Kernel
from cosmos_health import HealthBoard
from cosmos_runner import Runner
k = Kernel(r"V:\A\Ai\COSMOS\live", worker="cutover")
board = HealthBoard(k).run()
jid = k.sched.submit("print('cosmos live: hello from the runner')", "high")
res = Runner(k.sched, k.paths.role("work"), "cutover").drain()
print(json.dumps({
    "ready": k.ready, "tree_id": k.paths.sentinel.tree_id,
    "health_verdict": board["verdict"],
    "health_control_red": board["negative_control_red"],
    "job_outcome": res[0]["outcome"] if res else None,
    "ledger_records": sum(1 for _ in k.ledger.verify()),
}))
