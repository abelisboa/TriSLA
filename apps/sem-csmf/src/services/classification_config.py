"""
Feature flag for SEM-CSMF slice classification modes.
"""

import os
from enum import Enum


class ClassificationMode(str, Enum):
    KEYWORD_FIRST = "keyword_first"
    HYBRID = "hybrid"
    ONTOLOGY_FIRST = "ontology_first"


def get_classification_mode() -> ClassificationMode:
    raw = os.getenv("TRISLA_SEM_CLASSIFICATION_MODE", "keyword_first").strip().lower()
    try:
        return ClassificationMode(raw)
    except ValueError:
        return ClassificationMode.KEYWORD_FIRST


def ontology_precedence(mode: ClassificationMode) -> bool:
    return mode in (ClassificationMode.HYBRID, ClassificationMode.ONTOLOGY_FIRST)
