"""Append-only JSONL trace. One run, one file. Replayable, greppable, honest."""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path


class Trace:
    def __init__(self, run_id: str | None = None, trace_dir: str = "traces") -> None:
        self.run_id = run_id or time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        self.dir = Path(trace_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.path = self.dir / f"{self.run_id}.jsonl"

    def event(self, kind: str, **fields) -> dict:
        rec = {"ts": round(time.time(), 3), "kind": kind, **fields}
        with self.path.open("a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text().splitlines() if line.strip()]


def latest(trace_dir: str = "traces") -> Path | None:
    files = sorted(Path(trace_dir).glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def pretty(path: Path) -> str:
    out = [f"trace: {path.name}", "-" * 62]
    for rec in [json.loads(l) for l in path.read_text().splitlines() if l.strip()]:
        kind = rec.get("kind", "?")
        rest = {k: v for k, v in rec.items() if k not in ("ts", "kind")}
        payload = json.dumps(rest, ensure_ascii=False)
        out.append(f"{kind:<10} {payload[:160]}")
    return "\n".join(out)
