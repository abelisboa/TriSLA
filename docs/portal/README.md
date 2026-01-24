# TriSLA Portal

This folder documents the public Portal components used to submit SLA requests and visualize outcomes.

## Components
- **Portal Backend** — REST API gateway for SLA submissions
- **Portal Frontend** — UI for operators and evaluators

## Typical flow
1. User submits a SLA request via the Portal UI
2. Portal Backend forwards the request to the Decision Engine pipeline
3. The decision outcome is returned and displayed in the UI
