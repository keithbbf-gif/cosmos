#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""builds.tensor — measurement brain for the multi-model coding farm.

Three modules, one store, no network:

    tensor_math  T[pair, domain, judge, scaffold, provider] estimators
    dbase        append-only JSONL authority -> sqlite projection -> read API
    grading      charter judge, dual-judge, model rater, cell writer

Canon carried in from cosmos/cosmos_porosity.py and
docs/arch/ORTHOGONAL_POROSITY.md: JSONL is authority, sqlite is a
rebuildable projection, GET never mkdir, UNMEASURED until observed, and
orthogonality is neither disagreement frequency nor unsigned |v|.
"""
from __future__ import annotations

__all__ = ["tensor_math", "dbase", "grading"]
