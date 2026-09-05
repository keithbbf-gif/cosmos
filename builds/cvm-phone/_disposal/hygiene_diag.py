from pathlib import Path

s = Path("builds/cvm-phone/cvm_phone_gate.py").read_text(encoding="utf-8")
c = s.split("# ---------------- half B")[1].split("# ---------------- the record")[0]
tests = {
    "CoreDouble_in_core": "CoreDouble" in c,
    "dead_loopback_in_core": "dead_loopback_base" in c,
    "drive_backslash": "V:\\" in s,
    "drive_forward": "V:/" in s,
    "bts_import": "import bts_" in s,
    "bts_from": "from bts_" in s,
    "owner_assign_key": 'audio_owner"] =' in s,
    "owner_assign_var": "audio_owner = " in s,
}
for k, v in tests.items():
    print(k, v)
for i, line in enumerate(s.splitlines(), 1):
    if "audio_owner = " in line or "V:/" in line or "V:\\" in line:
        print(i, repr(line))
