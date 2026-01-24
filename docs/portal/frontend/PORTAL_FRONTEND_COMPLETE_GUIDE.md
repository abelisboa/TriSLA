# Portal Frontend

**Role.** User interface for submitting SLA requests and visualizing decision results.

## Purpose and Responsibilities
- Collect SLA requirements from users via web forms
- Call Portal Backend endpoints for submission
- Present decision outcome and optional explanation fields (XAI)
- Display SLA lifecycle status and monitoring data
- Provide user authentication and session management (if enabled)

## What the Module Does Not Do
- Does not make admission decisions
- Does not process requests server-side (delegated to Portal Backend)
- Does not manage SLA lifecycle (delegated to SLA-Agent)

## Architecture Overview

The Portal Frontend is a web application (typically React/Next.js):
- **Input**: User interactions via web browser
- **Output**: HTTP requests to Portal Backend API
- **Protocol**: HTTP/HTTPS (REST API calls)

## Interfaces

### User Interface Components

- **SLA Submission Form**: Collects requirements (latency, throughput, reliability)
- **Decision Results View**: Displays decision outcome and justification
- **SLA Status Dashboard**: Shows lifecycle status and monitoring metrics
- **XAI Visualization**: Presents explainability artifacts (if available)

### API Integration

The frontend calls Portal Backend endpoints:
-  — Submit SLA request
-  — Retrieve SLA status
-  — Retrieve decision outcome

## Configuration

### Environment Variables
- : Portal Backend base URL (required)
- : API request timeout in milliseconds (default: 30000)

### Build Configuration

The frontend is built as a static web application:
```bash
cd apps/portal-frontend
npm install
npm run build
```

### Deployment Method

The Portal Frontend is deployed via Helm:
```bash
helm upgrade --install trisla ./helm/trisla -n trisla -f ./helm/trisla/values.yaml
```

## Runtime Behavior

1. User accesses Portal Frontend via web browser
2. User fills SLA submission form
3. Frontend validates form data client-side
4. Frontend calls Portal Backend API to submit request
5. Frontend displays decision outcome and explanation

## Observability Hooks

- **Browser console logs**: Client-side error logging
- **API call metrics**: Tracked via Portal Backend observability

## Known Issues & Resolved Errors

### Issue: Requests fail due to wrong backend URL
**Symptom**: Frontend cannot reach backend API  
**Resolution**: Verify environment configuration used during build and deployment. Ensure  is correctly set.

### Issue: CORS errors
**Symptom**: Browser blocks API requests  
**Resolution**: Verify  configuration in Portal Backend

## Integration with Other TriSLA Modules

- **Portal Backend**: Calls API endpoints for submission and status retrieval
- **Observability**: Client-side errors are logged and can be correlated with backend traces

## Troubleshooting

- If requests fail due to wrong backend URL: verify environment configuration used during build and deployment
- If CORS errors occur: verify Portal Backend CORS configuration
