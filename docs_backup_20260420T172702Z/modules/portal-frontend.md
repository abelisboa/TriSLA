# Portal Frontend Module

## Overview

Portal Frontend is the user interaction layer of TriSLA. It captures SLA requests and visualizes decision, lifecycle, metrics, and XAI outputs.

## Core Responsibilities

- Provide structured input forms for SLA submission
- Guide users through interpretation and submission workflow
- Display decision outcomes and lifecycle state
- Present metrics and XAI evidence returned by backend APIs

## Interaction Contract

Portal Frontend communicates with Portal Backend as the single orchestration authority:

- submit/interpret requests
- retrieve SLA status and metrics
- render final outputs for operators and researchers

## Formal Interaction Loop

`U -> S -> Decision -> O -> Visualization`

Where:

- `U`: user input
- `S`: structured SLA request
- `O`: output package (decision + metrics + XAI)

## Operational Constraints

- Depends on backend/API availability
- Visualization quality depends on response completeness
- Does not execute policy or infrastructure actions

## References

- `docs/portal/README.md`
- `docs/portal/model/interaction_model.md`
- `docs/portal/architecture/portal_architecture.md`
