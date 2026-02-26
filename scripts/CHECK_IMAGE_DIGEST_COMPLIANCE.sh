#!/usr/bin/env bash

# ==========================================================
# TriSLA - Image Digest Compliance Checker (Robust Version)
# ==========================================================

set -euo pipefail

# Detect project root dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(realpath "$SCRIPT_DIR/..")"

NAMESPACE="trisla"
RELEASE="trisla"
CHART_PATH="$PROJECT_ROOT/helm/trisla"
EXPECTED_REGISTRY="ghcr.io/abelisboa"

ERRORS=0

echo "=========================================================="
echo "TriSLA IMAGE DIGEST COMPLIANCE CHECK"
echo "Namespace: $NAMESPACE"
echo "Release:   $RELEASE"
echo "Chart:     $CHART_PATH"
echo "=========================================================="
echo

# ----------------------------------------------------------
# Validate chart path exists
# ----------------------------------------------------------

if [ ! -d "$CHART_PATH" ]; then
  echo "❌ Chart path not found: $CHART_PATH"
  exit 1
fi

# ----------------------------------------------------------
# 1️⃣ Validate Helm Rendered Images
# ----------------------------------------------------------

echo "[1/5] Checking rendered Helm images..."

RENDERED_IMAGES=$(helm template "$RELEASE" "$CHART_PATH" -n "$NAMESPACE" \
  | grep -E "image:" \
  | awk '{print $2}' \
  | tr -d '"' )

if [ -z "$RENDERED_IMAGES" ]; then
  echo "❌ No images found in Helm template."
  exit 1
fi

for IMG in $RENDERED_IMAGES; do
  echo "→ Checking: $IMG"

  if [[ "$IMG" == *":latest"* ]]; then
    echo "❌ ERROR: Image uses latest tag → $IMG"
    ((ERRORS++))
  fi

  if [[ "$IMG" != *@sha256:* ]]; then
    echo "❌ ERROR: Image does not use digest → $IMG"
    ((ERRORS++))
  fi

  if [[ "$IMG" != $EXPECTED_REGISTRY* ]]; then
    echo "⚠ WARNING: Image not using expected registry → $IMG"
  fi
done

echo

# ----------------------------------------------------------
# 2️⃣ Validate Live Cluster Images
# ----------------------------------------------------------

echo "[2/5] Checking running cluster images..."

LIVE_IMAGES=$(kubectl get pods -n "$NAMESPACE" \
  -o jsonpath='{range .items[*]}{range .status.containerStatuses[*]}{.imageID}{"\n"}{end}{end}' \
  2>/dev/null | sed 's|docker.io/||')

if [ -z "$LIVE_IMAGES" ]; then
  echo "⚠ WARNING: No running containers found."
else
  while read -r IMG; do
    echo "→ Running: $IMG"
    if [[ "$IMG" != *@sha256:* ]]; then
      echo "❌ ERROR: Running container without digest → $IMG"
      ((ERRORS++))
    fi
  done <<< "$LIVE_IMAGES"
fi

echo

# ----------------------------------------------------------
# 3️⃣ Drift Detection
# ----------------------------------------------------------

echo "[3/5] Checking Helm vs Cluster drift..."

RENDERED_SORTED=$(echo "$RENDERED_IMAGES" | sort)
LIVE_SORTED=$(echo "$LIVE_IMAGES" | sort)

if ! diff <(echo "$RENDERED_SORTED") <(echo "$LIVE_SORTED") >/dev/null 2>&1; then
  echo "⚠ WARNING: Drift detected between Helm and running cluster images."
else
  echo "✔ No drift detected."
fi

echo

# ----------------------------------------------------------
# 4️⃣ Direct docker.io Detection
# ----------------------------------------------------------

echo "[4/5] Checking for docker.io usage in chart..."

if grep -R "docker.io" "$CHART_PATH" >/dev/null 2>&1; then
  echo "⚠ WARNING: docker.io references found in chart."
else
  echo "✔ No docker.io hardcoded references."
fi

echo

# ----------------------------------------------------------
# 5️⃣ Final Status
# ----------------------------------------------------------

echo "[5/5] Compliance Summary"

if [ "$ERRORS" -gt 0 ]; then
  echo "=========================================================="
  echo "❌ COMPLIANCE FAILED - $ERRORS issue(s) detected."
  echo "=========================================================="
  exit 1
else
  echo "=========================================================="
  echo "✔ FULLY COMPLIANT - All images use digest and are stable."
  echo "=========================================================="
fi
