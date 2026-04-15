# Portal Frontend

## Overview

Portal Frontend is the user-facing web layer for SLA lifecycle interactions. It
provides forms, workflow views, and status pages that expose TriSLA behavior to
operators and tenants.

## Role in TriSLA

The module acts as the northbound interaction surface for creating and tracking
SLA requests. It does not execute policy decisions directly; it orchestrates user
input and visualizes backend outputs.

## Interaction with Portal Backend

Portal Frontend calls Portal Backend APIs for:

- SLA interpretation and submission flows;
- status and metrics retrieval;
- lifecycle and observability views.

Portal Backend remains the authoritative orchestration and response layer.

## UI Responsibilities

- capture intent and SLA form parameters;
- present decision/lifecycle outcomes;
- provide operational visibility across modules.

## Telecom Context

In 5G slicing workflows, the frontend translates service-level requirements into
operator actions and presents admission/compliance outcomes in an understandable
workflow.

## Limitations

- depends on Portal Backend/API availability;
- UI fidelity is bounded by data exposed by backend endpoints;
- does not replace module-level observability tooling.
