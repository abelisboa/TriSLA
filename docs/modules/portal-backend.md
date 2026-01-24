# Portal Backend

**Role.** Public entry point for SLA submission. It validates request schemas and forwards them to the TriSLA decision pipeline.

## Responsibilities
- Accept user-facing SLA requests (template + form values)
- Provide consistent correlation fields for tracing (intent_id)
- Return the decision response to the UI

## Troubleshooting
- `ERR_NAME_NOT_RESOLVED` in browser: validate NodePort, DNS resolution, and the configured backend base URL in the frontend.
