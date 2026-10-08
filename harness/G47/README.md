Applied 2026-10-08 onto this tree from the streams folder. The streams original stays in place. Nothing here writes live/ or takes CCR.lease.
# G47

One planner for a COSMOS / COSMOS CODE harness call. It builds the pack, the argv, and the token cap. It does not start a model unless you call `execute`, and several doors refuse that on purpose.

Read `ARCHITECTURE.md` for the design and the seating scars it encodes. Read `CODE.md` for the module walk.

```
py -3.14 -m pytest tests\test_g47.py
py -3.14 -m g47 doctor
py -3.14 -m g47 plan --door opencode --role CODER --model inclusionai/ling-3.0-flash --window 262144 --where V:\tmp\attempt --task "Say the contract."
py -3.14 -m g47 grade --role CODER --what text --mouth -
```

`plan` prints JSON and does not spawn. `grade` exits 2 when the mouth fails its contract. This tree is not the live COSMOS checkout. Do not copy it into `V:\A` from here.
