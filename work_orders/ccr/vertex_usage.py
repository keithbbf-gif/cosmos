#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vertex_usage.py — real-time Vertex AI token consumption via Cloud Monitoring.

Fixes vs the pasted draft:
  * Valid metric types: aiplatform.googleapis.com/consumed_input_tokens and
    consumed_output_tokens (the draft's "://googleapis.com" is not a metric).
  * Token series are CUMULATIVE — aligned with ALIGN_DELTA + summed, so the
    total is tokens consumed in the window, not a running counter.
  * Per-model breakdown via the model label.

Auth: needs a credential with monitoring.read-only (service account key or
OAuth consent). The Vertex API keys (AaaAQ.) cannot call Monitoring.

Usage:
    py -3.14 vertex_usage.py --project project-5a33f910-1251-4d6a-bf9 --days 7
    py -3.14 vertex_usage.py --project project-5a33f910-1251-4d6a-bf9 --days 7 --per-model
"""
from __future__ import annotations

import argparse
import datetime

from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import Aggregation, TimeInterval

INPUT_METRIC = "aiplatform.googleapis.com/consumed_input_tokens"
OUTPUT_METRIC = "aiplatform.googleapis.com/consumed_output_tokens"


def fetch_tokens(client, project_name: str, metric_type: str,
                 interval: TimeInterval, per_model: bool) -> dict[str, int]:
    """Return {label: total_tokens} for one metric over the interval."""
    aggregation = Aggregation(
        alignment_period={"seconds": 86400},
        per_series_aligner=Aggregation.Aligner.ALIGN_DELTA,
        cross_series_reducer=Aggregation.Reducer.REDUCE_SUM,
        group_by_fields=["metric.label.model"] if per_model else [],
    )
    results = client.list_time_series(
        request={
            "name": project_name,
            "filter": f'metric.type = "{metric_type}"',
            "interval": interval,
            "aggregation": aggregation,
            "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
        }
    )
    totals: dict[str, int] = {}
    for ts in results:
        label = ts.resource.labels.get("model") or "all"
        if per_model:
            label = ts.metric.labels.get("model") or "unknown"
        for point in ts.points:
            v = point.value.int64_value or 0
            totals[label] = totals.get(label, 0) + v
    return totals


def main() -> None:
    ap = argparse.ArgumentParser(description="Vertex AI token usage via Cloud Monitoring")
    ap.add_argument("--project", required=True, help="GCP project id")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--per-model", action="store_true", help="Break down by model label")
    args = ap.parse_args()

    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{args.project}"

    now = datetime.datetime.now(datetime.timezone.utc)
    start = now - datetime.timedelta(days=args.days)
    interval = TimeInterval(
        {"end_time": {"seconds": int(now.timestamp())},
         "start_time": {"seconds": int(start.timestamp())}}
    )

    print(f"Project {args.project} | last {args.days} days")
    for name, metric in (("INPUT", INPUT_METRIC), ("OUTPUT", OUTPUT_METRIC)):
        try:
            totals = fetch_tokens(client, project_name, metric, interval, args.per_model)
            grand = sum(totals.values())
            print(f"\n{name} tokens: {grand:,}")
            if args.per_model:
                for model, n in sorted(totals.items(), key=lambda x: -x[1]):
                    print(f"  {model:<40} {n:,}")
        except Exception as e:  # noqa: BLE001
            print(f"\n{name} FAILED: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()