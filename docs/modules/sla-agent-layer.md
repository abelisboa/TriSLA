# Sla Agent Layer

## Overview

This module is part of the TriSLA v3.9.3 architecture.

## Purpose

Encaminha ingestão de eventos de pipeline e avaliação SLO para o ecossistema TriSLA; em ambientes sem Kafka consumidor ativo, o ingest HTTP (`POST /api/v1/ingest/pipeline-event`) complementa o fluxo. O Portal Backend pode acionar ingest com timeout alargado quando `SLA_AGENT_INGEST_RUN_SLO=true`.

## Evidence — full closure campaign

A campanha em `scripts/e2e/trisla_full_closure_campaign.py` verifica a presença de `intent_id` nos logs de `trisla-sla-agent-layer` após cada submit, em conjunto com SEM, ML-NSMF, Decision Engine, NASP e BC-NSSMF.

## Configuration

See module README for configuration details.

## Telemetry alignment note

- The SLA-Agent layer consumes pipeline evidence and SLO-oriented metrics for lifecycle tracking.
- It is not the primary decision-policy module; final SLA admission remains governed upstream by Decision Engine policy plus ML risk outputs.

## Version

Part of TriSLA v3.9.3 (frozen scientific version).
