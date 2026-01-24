# Portal Frontend

**IMPORTANT**: The Portal Frontend is a visualization and interaction layer, not part of the TriSLA control logic. It provides a web-based interface for users to submit SLA requests and view decision outcomes, but does not implement any business logic or decision-making capabilities.

## Purpose

The Portal Frontend exists to:

1. **Collect User Input**: Provide web forms for users to submit SLA requirements (via template or natural language)
2. **Display Decision Outcomes**: Present decision results (ACCEPT, RENEG, REJECT) with justification and blockchain data
3. **Monitor SLA Status**: Show SLA lifecycle status and real-time metrics
4. **Visualize Module Health**: Display health status of TriSLA modules
5. **Present XAI Artifacts**: Display explainability artifacts when available

## What It Does NOT Do

- **Does not implement business logic** (delegated to Portal Backend and TriSLA modules)
- **Does not make admission decisions** (Decision Engine responsibility)
- **Does not process semantic intent** (SEM-CSMF responsibility)
- **Does not perform ML predictions** (ML-NSMF responsibility)
- **Does not manage SLA lifecycle** (SLA-Agent responsibility)
- **Does not register on-chain** (BC-NSSMF responsibility)
- **Does not process requests server-side** (all processing delegated to Portal Backend)

## Relationship to Portal Backend

The Portal Frontend is a **thin client** that:

- Makes HTTP requests to Portal Backend REST API
- Displays responses from Portal Backend
- Handles user interactions and form validation (client-side only)
- Manages UI state and navigation

All business logic, validation, and orchestration is handled by Portal Backend.

## Supported Workflows

### SLA Submission

1. **Template-based Submission**: User selects a template (URLLC, eMBB, mMTC) and fills form fields
2. **Natural Language Submission**: User enters intent text in natural language (PLN)
3. **Form Validation**: Client-side validation of required fields and formats
4. **API Call**: Frontend calls  or 
5. **Result Display**: Frontend displays decision outcome and redirects to result page

### Monitoring

1. **Status Retrieval**: Frontend calls  to retrieve lifecycle status
2. **Metrics Retrieval**: Frontend calls  to retrieve performance metrics
3. **Auto-refresh**: Frontend polls status/metrics endpoints at configurable intervals

## Technical Stack

- **Framework**: Next.js 15 (React 18)
- **State Management**: Zustand
- **API Client**: Custom  function using native  API
- **Styling**: Tailwind CSS with Radix UI components
- **Build**: Next.js standalone output for containerized deployment

## Deployment

The Portal Frontend is deployed via Helm as part of the TriSLA Portal chart:



Configuration is provided through Helm values under  section in .

## Observability

- **Browser Console Logs**: Client-side errors and API call failures
- **Network Traces**: Browser DevTools network tab shows all API requests/responses
- **Error Boundaries**: React error boundaries catch and log component errors

## Documentation

- **[Complete Guide](PORTAL_FRONTEND_COMPLETE_GUIDE.md)** — Comprehensive technical documentation
- **[Architecture Overview](../../ARCHITECTURE.md)** — System-level architecture
- **[Deployment Guide](../../DEPLOYMENT.md)** — Deployment procedures

## Implementation Basis

This documentation is based on the real TriSLA implementation in  and deployment configuration in .
