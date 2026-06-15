"""
Entity Linker - SEM-CSMF
Maps natural language intent text to OWL UseCaseSlice individuals.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from opentelemetry import trace

tracer = trace.get_tracer(__name__)

TRISLA_NS = "http://trisla.org/ontology#"


@dataclass
class LinkResult:
    individual: str
    slice_type: str
    confidence: float
    method: str


class EntityLinker:
    """Text → OWL individual → slice type via TTL ABox aliases."""

    def __init__(self, ontology_loader):
        self._loader = ontology_loader
        self._alias_entries: List[Tuple[str, str]] = []
        self._slice_types: Dict[str, str] = {}
        self._built = False

    def initialize(self) -> None:
        if self._built:
            return
        with tracer.start_as_current_span("entity_linker_initialize") as span:
            self._alias_entries = []
            self._slice_types = {}
            index = self._loader.get_abox_index()
            for individual, data in index.items():
                slice_type = data.get("slice_type")
                if slice_type:
                    self._slice_types[individual] = slice_type
                for alias in data.get("aliases", []):
                    normalized = _normalize_text(alias)
                    if normalized:
                        self._alias_entries.append((normalized, individual))
            self._alias_entries.sort(key=lambda item: len(item[0]), reverse=True)
            self._built = True
            span.set_attribute("entity_linker.individuals", len(self._slice_types))
            span.set_attribute("entity_linker.aliases", len(self._alias_entries))

    def link(self, intent_text: str) -> Optional[LinkResult]:
        if not self._built:
            self.initialize()
        if not intent_text or not intent_text.strip():
            return None

        normalized_text = _normalize_text(intent_text)
        with tracer.start_as_current_span("entity_linker_link") as span:
            span.set_attribute("intent_text.length", len(intent_text))

            for alias, individual in self._alias_entries:
                if alias in normalized_text:
                    slice_type = self._slice_types.get(individual)
                    if slice_type:
                        span.set_attribute("entity_linker.individual", individual)
                        span.set_attribute("entity_linker.slice_type", slice_type)
                        return LinkResult(
                            individual=individual,
                            slice_type=slice_type,
                            confidence=1.0,
                            method="alias_substring",
                        )

            best: Optional[Tuple[str, str, float]] = None
            text_tokens = set(normalized_text.split())
            for alias, individual in self._alias_entries:
                alias_tokens = set(alias.split())
                if not alias_tokens:
                    continue
                overlap = len(text_tokens & alias_tokens) / len(alias_tokens)
                if overlap >= 0.7 and (best is None or overlap > best[2]):
                    slice_type = self._slice_types.get(individual)
                    if slice_type:
                        best = (individual, slice_type, overlap)

            if best:
                individual, slice_type, overlap = best
                span.set_attribute("entity_linker.individual", individual)
                span.set_attribute("entity_linker.slice_type", slice_type)
                return LinkResult(
                    individual=individual,
                    slice_type=slice_type,
                    confidence=overlap,
                    method="token_overlap",
                )

            return None


def _normalize_text(text: str) -> str:
    lowered = text.lower().strip()
    normalized = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    collapsed = re.sub(r"\s+", " ", without_accents)
    return collapsed.strip()
