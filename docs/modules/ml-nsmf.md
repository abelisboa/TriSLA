# Ml Nsmf

## Overview

This module is part of the TriSLA v3.9.3 architecture.

## Purpose

[Module-specific purpose - to be detailed]

## Configuration

See module README for configuration details.

## Jitter Usage in TriSLA

Jitter is incorporated as part of SLA requirements and is used as an input feature for machine learning risk estimation.

It influences the predicted risk score but does not directly trigger decision thresholds.

## Telemetry role alignment

- ML features include SLA-defined latency, SLA-defined reliability, and SLA-defined jitter.
- Runtime transport jitter remains primarily a contextual/observability signal unless mapped into explicit model features for a given experiment.

## Version

Part of TriSLA v3.9.3 (frozen scientific version).
