"""Shadow log sink implementations (Phase 33)."""

from __future__ import annotations

import json
import logging
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, TextIO

logger = logging.getLogger(__name__)


class ShadowLogSink(ABC):
    @abstractmethod
    def write(self, event: Dict[str, Any]) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...


class NullShadowLogSink(ShadowLogSink):
    """No-op sink when shadow logger is disabled."""

    def write(self, event: Dict[str, Any]) -> None:
        return

    def close(self) -> None:
        return


class FileShadowLogSink(ShadowLogSink):
    def __init__(self, base_path: str, run_id: str):
        self._dir = Path(base_path) / run_id
        self._dir.mkdir(parents=True, exist_ok=True)
        self._events_path = self._dir / "shadow_foundation_events.jsonl"
        self._manifest_path = self._dir / "shadow_run_manifest.json"

    def write(self, event: Dict[str, Any]) -> None:
        line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self._events_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def write_manifest(self, manifest: Dict[str, Any]) -> None:
        self._manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @property
    def events_path(self) -> Path:
        return self._events_path

    def close(self) -> None:
        return


class StdoutShadowLogSink(ShadowLogSink):
    def __init__(self, stream: TextIO | None = None):
        self._stream = stream or sys.stdout

    def write(self, event: Dict[str, Any]) -> None:
        line = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        self._stream.write(line + "\n")
        self._stream.flush()

    def close(self) -> None:
        return


class OtlpShadowLogSink(ShadowLogSink):
    """OTLP sink stub — disabled by default (Phase 33 foundation)."""

    def __init__(self, enabled: bool = False):
        self._enabled = enabled
        self._buffer: list[Dict[str, Any]] = []

    def write(self, event: Dict[str, Any]) -> None:
        if not self._enabled:
            logger.debug("[SHADOW] OTLP sink disabled; event buffered only in memory")
        self._buffer.append(event)

    @property
    def buffer(self) -> list[Dict[str, Any]]:
        return list(self._buffer)

    def close(self) -> None:
        return


def create_sink(
    sink_name: str,
    log_path: str,
    run_id: str,
    otlp_enabled: bool,
    *,
    enabled: bool = True,
) -> ShadowLogSink:
    if not enabled:
        return NullShadowLogSink()
    name = (sink_name or "file").strip().lower()
    if name == "stdout":
        return StdoutShadowLogSink()
    if name == "otlp":
        return OtlpShadowLogSink(enabled=otlp_enabled)
    return FileShadowLogSink(log_path, run_id)
