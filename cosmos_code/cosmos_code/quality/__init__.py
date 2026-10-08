"""Quality spine. Draft does not run until Shot-1 evidence is in the log."""

from cosmos_code.quality.ladder import GateFailure, GateUnavailable, ladder_from_rows

__all__ = ["GateFailure", "GateUnavailable", "ladder_from_rows"]
