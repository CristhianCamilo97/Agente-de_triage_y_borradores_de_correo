# Medicion de costo por request (precios de referencia Haiku; ajusta si cambian).

from __future__ import annotations

import json
import time
from pathlib import Path

# USD por millon de tokens (referencia didactica; no es factura real de AWS).
PRICES = {
    "claude-haiku-4-5": {
        "input": 1.0,
        "output": 5.0,
        "cache_write": 1.25,
        "cache_read": 0.1,
    }
}

LOG = Path(__file__).resolve().parent / "resultados" / "usage.jsonl"


def _alias(model: str) -> str:
    for a in PRICES:
        if a in model:
            return a
    return "claude-haiku-4-5"


def cost_usd(usage, model: str, batch: bool = False) -> float:
    p = PRICES[_alias(model)]
    inp = getattr(usage, "input_tokens", 0) or 0
    out = getattr(usage, "output_tokens", 0) or 0
    cw = getattr(usage, "cache_creation_input_tokens", 0) or 0
    cr = getattr(usage, "cache_read_input_tokens", 0) or 0
    total = (inp * p["input"] + out * p["output"] + cw * p["cache_write"] + cr * p["cache_read"]) / 1_000_000
    if batch:
        total *= 0.5
    return round(total, 6)


def log_usage(feature: str, model: str, usage, latency_ms: float = 0.0, **extra) -> dict:
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "feature": feature,
        "model": model,
        "input_tokens": getattr(usage, "input_tokens", 0) or 0,
        "output_tokens": getattr(usage, "output_tokens", 0) or 0,
        "cache_write": getattr(usage, "cache_creation_input_tokens", 0) or 0,
        "cache_read": getattr(usage, "cache_read_input_tokens", 0) or 0,
        "cost_usd": cost_usd(usage, model),
        "latency_ms": round(latency_ms, 1),
        **extra,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
