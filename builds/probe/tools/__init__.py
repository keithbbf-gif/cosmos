# -*- coding: utf-8 -*-
"""COSMOS tools/ surface — F-29 prototype, fenced under builds/probe/tools/.

Repo-root `tools/` does not exist; this directory is the in-fence prototype.
Promotion into `tools/` or `cosmos/` is COW's. Registration is not capability:
`inventory()` lists declarations, `invoke()` is the measurement.
"""
from .surface import ToolError, ToolSpec, ToolSurface  # noqa: F401
from .mcp_docs import MCP_DOCS, make_surface  # noqa: F401
