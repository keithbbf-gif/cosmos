# -*- coding: utf-8 -*-
"""COSMOS tools/ surface — F-29.

A tool is a named verb. Registration is not capability: `inventory()` lists
declarations, `invoke()` is the measurement. Kernel composes this package
as the `tools-surface` row (fail-open, no invoke on boot).
"""
from .surface import ToolError, ToolSpec, ToolSurface  # noqa: F401
from .mcp_docs import MCP_DOCS, attach_to_kernel, make_surface  # noqa: F401
