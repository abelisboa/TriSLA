# TriSLA v3.9.3 - Frozen Images Contract (Scientific Publication)

**This document is normative and authoritative for TriSLA v3.9.3 scientific publication.**

**Publication Date**: 2026-01-23
**Cluster**: NASP
**Namespace**: trisla
**Scientific Version**: v3.9.3
**Codebase Version**: v3.9.4 (tagged as v3.9.3 for publication)

## ✅ CRITICAL: Scientific Freeze - COMPLETED

**This contract represents a FROZEN state for scientific publication.**

- **NO logic changes** are permitted without new experiments
- **NO threshold modifications** are permitted
- **NO semantic changes** are permitted
- All results from Chapter 6 derive from these exact images

## ✅ Mandatory Images (All Published)

### Core Services

| Module | Image | Tag | Status | Digest |
|--------|-------|-----|--------|--------|
| SEM-CSMF | ghcr.io/abelisboa/sem-csmf | v3.9.3 | ✅ Published | 128e84508fdd |
| ML-NSMF | ghcr.io/abelisboa/ml-nsmf | v3.9.3 | ✅ Published | 8b759c84cb21 |
| Decision Engine | ghcr.io/abelisboa/decision-engine | v3.9.3 | ✅ Published | 72542d503d22 |
| BC-NSSMF | ghcr.io/abelisboa/bc-nssmf | v3.9.3 | ✅ Published | 25161bba7436 |
| SLA-Agent | ghcr.io/abelisboa/sla-agent | v3.9.3 | ✅ Published | d78a463ae370 |

### Portal Components

| Module | Image | Tag | Status | Digest |
|--------|-------|-----|--------|--------|
| Portal Backend | ghcr.io/abelisboa/portal-backend | v3.9.3 | ✅ Published | f3468bb0087a |
| Portal Frontend | ghcr.io/abelisboa/portal-frontend | v3.9.3 | ✅ Published | 9cba6b347b85 |

## Compatibility Tags

All images also available with trisla- prefix for Helm compatibility:
-  (for each module above)

## Image Sources

All images built from:
- **Codebase**: v3.9.4 codebase
- **Tagged as**: v3.9.3 for scientific publication
- **Build Date**: 2026-01-23
- **Registry**: ghcr.io/abelisboa
- **Status**: ✅ All images published and pullable

## Prohibition of Alteration

**Without new experiments, the following are PROHIBITED**:
- Changing image tags
- Modifying image contents
- Updating to newer versions
- Altering deployment configurations that affect results

## Reproducibility Guarantee

This contract guarantees that:
1. ✅ All Chapter 6 results can be reproduced using these exact images
2. ✅ Third parties can deploy TriSLA using only these images
3. ✅ Scientific claims are verifiable and reproducible

## Publication Readiness

- [x] All 7 images built
- [x] All 7 images pushed to ghcr.io
- [x] All images verified pullable
- [x] Helm values updated to v3.9.3
- [x] Documentation complete
- [x] No private dependencies

**Status**: ✅ **COMPLETE - READY FOR PUBLICATION**
