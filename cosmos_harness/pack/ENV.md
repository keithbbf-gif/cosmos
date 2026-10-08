# L7 environment

Path policy is Python (`jail.py`). The process tree is C
(`native/job_object.c`), loaded from Python when the tests run.
`wipe_proof` stays false. Reason stays `policy_only`.

Attempt root: {{WHERE}}
live/ is refused.
Oracle argv: {{ORACLE}}
