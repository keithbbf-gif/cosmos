# SPIKE FINDINGS - cosmos_paths (F5 builder) - 2026-08-23

## MEASURED, NATIVE (Windows, py -3.14)

Selftest output from the native queue-lane run:

```
[stderr]Switched to a new branch 'spike/cosmos_paths-f5'
```

## WHAT HELD
- Sentinel CONTENT verification catches the existing-but-empty-directory trap that
  defeated isdir() guards in the incumbent (the mesh() scar) - asserted by a planted
  negative control, BY KIND.
- Typed absence works as an exception carrying `kind`; the selftest asserts the KIND,
  not merely that something raised - a wrong kind is a failure.
- Settability proven structurally: two installs at different roots, different depths,
  no shared state, same class.
- MAX_PATH: a >400-char path was created, written, read, and walked through extended() on native Windows.
- MEASURED SURPRISE (first run FAILED on it): MAX_PATH bites at CREATION - pathlib.mkdir(parents=True)
  un-prefixed returned WinError 206/3 building the test tree itself; os.makedirs(extended(p)) succeeds.
  EVERY mkdir(parents=True) in the 139 ported tools is a suspect; the platform adapter must own
  directory CREATION, not just reads and walks.
- Explicit instantiation: importing the module performs no resolution; construction
  IS verification; there is no half-built resolver state.

## WHAT THE BULK PORT MUST CARRY
- Role table is ONE declaration; callers never assemble paths. Unknown role REFUSES.
- from_install_record() refuses when no record is given - no guessing, no ladder.
- extended() must be applied by the platform adapter on EVERY walk/stat/open in the
  ported tools, not left to caller discipline.

## HONEST LIMITS
- This spike does not implement the install-record ACL or the tree_id provisioning
  flow (installer work, 6b).
- UNC extended-length form is implemented but NOT measured here (no UNC path on this
  machine tonight): NATIVE-DEMO-REQUIRED remains open for UNC.
