# builds/cdeck — in-tree binders (no submodule)

`builds/cdeck` was previously recorded as a **gitlink** (`mode 160000`, commit
`f4270d0953a5e2b8d17b33aac3fe826e8767e86a`) with **no** `.gitmodules` entry.
A plain `git checkout` therefore left an **empty directory**, and Core’s lazy
imports of `cosmos_*_panel` failed with `CDECK_PANEL_NOT_COMPOSED` (503).

**Decision:** vendor the Core route binders as normal tracked files under this
path. Do **not** re-add `.gitmodules` or pin the old submodule commit; the
external cDeck product tree remains at `keithbbf-gif/cdeck` for Gitur, not
as a nested submodule here.

**Recovered from:** unmerged history (`cursor/b7-015` fleet blob; `cursor/b6-004-opened`
/ `10bf873` for jukebox · nodemap · recents).
