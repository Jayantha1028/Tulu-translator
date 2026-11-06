"""
kannada_tigalari_converter.core.observability
=============================================
Lightweight structured logging ring buffer, latency percentile tracker (P95/P99),
and request telemetry for Tulu translation, ASR, and OCR services.
"""

from __future__ import annotations

import collections
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class StructuredLogger:
    """Thread-safe circular ring buffer storing up to `max_entries` structured logs."""

    def __init__(self, max_entries: int = 1000):
        self._buffer: collections.deque = collections.deque(maxlen=max_entries)
        self._lock = threading.Lock()

    def log(
        self,
        service: str,
        level: str,
        event: str,
        message: str,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        **extra: Any,
    ) -> Dict[str, Any]:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": service,
            "level": level.upper(),
            "event": event,
            "message": message,
            "correlation_id": correlation_id,
            "duration_ms": duration_ms,
            "extra": extra,
        }
        with self._lock:
            self._buffer.append(entry)
        return entry

    def tail(self, limit: int = 50, service: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            entries = list(self._buffer)
        if service:
            entries = [e for e in entries if e["service"] == service]
        return entries[-limit:]


class TelemetryTracker:
    """Sliding-window latency tracker computing P95, P99, RPS, and error percentages."""

    def __init__(self, window_seconds: int = 60):
        self.window_seconds = window_seconds
        self._samples: collections.deque = collections.deque()
        self._lock = threading.Lock()

    def record(self, duration_ms: float, status_code: int = 200) -> None:
        now = time.time()
        with self._lock:
            self._samples.append((now, duration_ms, status_code))
            cutoff = now - self.window_seconds
            while self._samples and self._samples[0][0] < cutoff:
                self._samples.popleft()

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            now = time.time()
            cutoff = now - self.window_seconds
            valid = [s for s in self._samples if s[0] >= cutoff]

        total = len(valid)
        if total == 0:
            return {
                "request_count": 0,
                "rps": 0.0,
                "error_rate_pct": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "min_latency_ms": 0.0,
                "max_latency_ms": 0.0,
            }

        latencies = sorted(s[1] for s in valid)
        errors = sum(1 for s in valid if s[2] >= 400)
        p95_idx = int(total * 0.95)
        p99_idx = int(total * 0.99)

        return {
            "request_count": total,
            "rps": round(total / float(self.window_seconds), 2),
            "error_rate_pct": round((errors / total) * 100.0, 2),
            "p95_latency_ms": round(latencies[min(p95_idx, total - 1)], 2),
            "p99_latency_ms": round(latencies[min(p99_idx, total - 1)], 2),
            "min_latency_ms": round(latencies[0], 2),
            "max_latency_ms": round(latencies[-1], 2),
        }


# Global instances for unified application monitoring
GLOBAL_LOGGER = StructuredLogger(max_entries=1000)
GLOBAL_TELEMETRY = TelemetryTracker(window_seconds=60)
