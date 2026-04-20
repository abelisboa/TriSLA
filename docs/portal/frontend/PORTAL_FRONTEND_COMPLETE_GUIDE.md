# Portal Frontend Complete Guide

This document provides comprehensive technical documentation for the Portal Frontend module, based on the real TriSLA implementation.

## 1. Design Purpose and Constraints

### Purpose

The Portal Frontend is a presentation and interaction layer that enables users to interact with the TriSLA system through a web browser. It serves as a thin client that:

- Collects user input via web forms
- Displays decision outcomes and status information
- Provides navigation and workflow guidance
- Visualizes data from Portal Backend API responses

### Constraints

The Portal Frontend is explicitly **not** part of the TriSLA control logic:

- **No Business Logic**: All business logic is delegated to Portal Backend
- **No Server-Side Processing**: All processing happens in Portal Backend
- **Stateless Client**: Frontend maintains only UI state, not application state
- **API-Driven**: All data comes from Portal Backend REST API calls
- **Presentation Only**: Frontend formats and displays data, but does not interpret or transform it

### Design Principles

1. **Separation of Concerns**: Frontend handles presentation, Backend handles logic
2. **API Contract Compliance**: Frontend strictly adheres to Portal Backend API contracts
3. **Error Propagation**: Errors from Backend are displayed to users without modification
4. **Traceability**: All API calls include correlation IDs for end-to-end tracing

## 2. Frontend Architecture

### Component Structure



### Framework and Libraries

- **Next.js 15**: React framework with App Router
- **React 18**: UI library
- **Zustand**: State management for global application state
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Zod**: Schema validation (if used for form validation)

### File Structure



### API Client Implementation

The API client () provides:

- **apiFetch()**: Wrapper around native  API with:
  - 30-second timeout
  - Automatic error parsing
  - JSON response handling
  - AbortController for request cancellation
- **apiClient**: Object with convenience methods:
  - 
  - 
  - 
  - 
  - etc.

### Next.js Rewrites

The  file configures API rewrites:

/:path*

This allows the frontend to make same-origin requests to , which are proxied to Portal Backend.

## 3. API Interaction Model

### API Base URL Configuration

The frontend uses a relative API base URL () that is rewritten by Next.js to the Portal Backend service:

- **Development**:  (from )
- **Production**:  (from  environment variable)

### API Calls Made by Frontend

#### POST /api/v1/sla/submit

**Purpose**: Submit SLA request through full TriSLA pipeline

**Request Payload**:


**Response Handling**:
- On success: Extract , , redirect to 
- On error: Display error message from 

**Implementation**: 

#### POST /api/v1/sla/interpret

**Purpose**: Interpret SLA intent using SEM-CSMF only

**Request Payload**:


**Response Handling**:
- Display interpreted intent and technical parameters
- Allow user to adjust parameters before submission

**Implementation**: 

#### GET /api/v1/sla/status/{sla_id}

**Purpose**: Retrieve SLA lifecycle status

**Response Handling**:
- Display status: , , , , , 
- Show , , , 

**Implementation**: , 

#### GET /api/v1/sla/metrics/{sla_id}

**Purpose**: Retrieve SLA performance metrics

**Response Handling**:
- Display metrics: , , , , , 
- Auto-refresh at configurable intervals (default: 30 seconds)

**Implementation**: 

#### GET /api/v1/modules

**Purpose**: Retrieve list of TriSLA modules and their health status

**Response Handling**:
- Display module list with health indicators
- Link to module detail pages

**Implementation**: , 

#### GET /api/v1/health/global

**Purpose**: Retrieve global health status

**Response Handling**:
- Display overall system health
- Show module-by-module status

**Implementation**: 

### Error Handling Strategy

The frontend handles errors in a standardized way:

1. **API Errors**: Caught by , converted to :
   

2. **Network Errors**: Timeout (30s) or connection failures → Display Timeout ao conectar com o backend or Erro ao conectar com o backend

3. **HTTP Errors**: 4xx/5xx responses → Extract  from JSON response, display to user

4. **Client-Side Errors**: React error boundaries catch component errors, log to console

### Request Timeout

All API requests have a 30-second timeout configured via :



## 4. User-to-Control-Plane Interaction Flow

### Template-Based SLA Submission Flow

1. **User Navigation**: User navigates to 

2. **Template Selection**: User selects a template (URLLC, eMBB, mMTC) from predefined list

3. **Form Rendering**: Frontend renders form fields based on selected template:
   - URLLC:  (ms),  (%)
   - eMBB:  (Mbps),  (Mbps)
   - mMTC:  (per km²),  (years)

4. **Form Validation**: Client-side validation:
   - Required fields check
   - Numeric range validation (min/max)
   - Format validation

5. **Form Submission**: User clicks submit button

6. **API Call**: Frontend calls  with:
   

7. **Response Handling**:
   - **Success**: Extract , , redirect to 
   - **Error**: Display error message, keep user on form page

8. **Result Display**: User views decision outcome on  page

### Natural Language Submission Flow

1. **User Navigation**: User navigates to 

2. **Intent Input**: User enters intent text in natural language

3. **Interpretation Request**: User clicks Interpret button

4. **API Call**: Frontend calls  with:
   

5. **Interpretation Display**: Frontend displays:
   - Interpreted  (URLLC, eMBB, mMTC)
   - Extracted 
   - Suggested 

6. **Parameter Adjustment**: User can adjust technical parameters

7. **Submission**: User clicks Submit → Calls  with adjusted parameters

8. **Result Display**: Same as template-based flow

### Monitoring Flow

1. **User Navigation**: User navigates to  or 

2. **Status Retrieval**: Frontend calls 

3. **Metrics Retrieval**: Frontend calls 

4. **Data Display**: Frontend displays:
   - Lifecycle status
   - Performance metrics (latency, throughput, packet loss, etc.)
   - Timestamp of last update

5. **Auto-Refresh**: Frontend polls endpoints at configurable intervals (default: 30 seconds)

## 5. Data Models and UI-State Mapping

### Request Payload Models

**SLASubmitRequest** (sent to Portal Backend):


**SLAInterpretRequest** (sent to Portal Backend):


### Response Payload Models

**SLASubmitResponse** (received from Portal Backend):


**SLAStatusResponse** (received from Portal Backend):


**SLAMetricsResponse** (received from Portal Backend):


### UI State Mapping

**Component State** (React ):
- Form field values
- Loading states
- Error messages
- Selected template
- Auto-refresh toggle

**Global State** (Zustand ):
- Module health status
- Global health status
- Loading flags
- Error messages

**URL State** (Next.js router):
-  (query parameter)
-  (query parameter)
- Current route

### State Flow

1. **User Input** → Component state ()
2. **Form Submission** → API call → Response → Component state update
3. **Navigation** → URL state update → Component re-render
4. **Global Data** → Zustand store → Components subscribe via 

## 6. Error Handling and User Feedback

### Error Types

1. **API Errors**: HTTP errors (4xx, 5xx) from Portal Backend
2. **Network Errors**: Connection failures, timeouts
3. **Validation Errors**: Client-side form validation failures
4. **Component Errors**: React component errors

### Error Display

**API Errors**:
- Error message displayed in UI (typically in a Card or Alert component)
- Error detail from  shown to user
- HTTP status code logged to console

**Network Errors**:
- Timeout ao conectar com o backend (for timeout)
- Erro ao conectar com o backend (for connection failure)
- User can retry the operation

**Validation Errors**:
- Field-level validation errors shown inline
- Form submission blocked until validation passes

**Component Errors**:
- React error boundaries catch errors
- Error logged to browser console
- Fallback UI displayed (if error boundary implemented)

### User Feedback Mechanisms

1. **Loading States**: Spinner or skeleton UI during API calls
2. **Success Messages**: Confirmation when operation succeeds
3. **Error Messages**: Clear error messages with actionable guidance
4. **Status Indicators**: Visual indicators for decision outcomes (ACCEPT/RENEG/REJECT)
5. **Auto-Refresh Feedback**: Visual indicator when metrics are being refreshed

### Error Recovery

- **Retry**: User can retry failed operations
- **Navigation**: User can navigate away and return
- **Form Reset**: User can reset form and start over

## 7. Deployment and Build Configuration

### Build Process

The frontend is built using Next.js:



**Build Output**: Next.js generates a standalone output in  directory, suitable for containerized deployment.

### Docker Build

The  builds the frontend:



### Environment Variables

**Build-time** ():
- : API base URL (default: )

**Runtime** (Helm values):
- : Portal Backend service URL (default: )

### Helm Configuration

The frontend is deployed via Helm chart ():



### Next.js Configuration

The  file configures:

- **Output Mode**:  (for containerized deployment)
- **API Rewrites**: Proxies  to Portal Backend
- **Server Actions**: Allows cross-origin server actions (if used)

### Deployment Steps

1. **Build Image**: 
2. **Push Image**: 
3. **Deploy via Helm**: 

## 8. Observability

### Logs Generated

**Browser Console Logs**:
- API call errors
- Component errors (if error boundaries catch them)
- Network failures
- Validation errors

**Example Log Format**:


### Browser Traces

**Network Tab** (Browser DevTools):
- All HTTP requests to 
- Request/response payloads
- Response times
- HTTP status codes
- Request headers

**Performance Tab**:
- Component render times
- API call durations
- Page load metrics

### Error Tracking

**Client-Side Errors**:
- React error boundaries catch component errors
- Errors logged to browser console
- No automatic error reporting to external services (unless configured)

**API Errors**:
- Errors from Portal Backend are displayed to users
- Error details logged to console for debugging
- Correlation IDs (if present) can be used for backend trace correlation

### Correlation with Backend

- **Request Headers**: Frontend can include correlation headers (if implemented)
- **Response Headers**: Backend may include trace IDs in response headers
- **URL Parameters**: ,  in URLs enable correlation

### Metrics

**Client-Side Metrics** (if implemented):
- Page load time
- API call latency
- Error rates
- User interaction events

**Backend Metrics**: All business metrics are tracked by Portal Backend, not Frontend.

## 9. Known Issues and Resolutions

### Issue: ERR_NAME_NOT_RESOLVED in Browser

**Symptom**: Browser console shows  when frontend tries to call API.

**Root Cause**: Frontend is trying to call  directly from browser, but this hostname only exists inside Kubernetes cluster.

**Resolution**:
1. Use Next.js rewrites to proxy API calls through Next.js server
2. Configure  environment variable correctly
3. Ensure  rewrites are configured to proxy  to Portal Backend

**Validation Evidence**: API calls succeed, network tab shows requests to  (same-origin), not to .

### Issue: CORS Errors

**Symptom**: Browser console shows CORS errors when frontend makes API calls.

**Root Cause**: Portal Backend CORS configuration does not allow frontend origin.

**Resolution**:
1. Configure Portal Backend CORS to allow frontend origin
2. Or use Next.js rewrites (same-origin, no CORS needed)

**Validation Evidence**: No CORS errors in browser console, API calls succeed.

### Issue: Timeout Errors

**Symptom**: API calls timeout after 30 seconds, user sees Timeout ao conectar com o backend.

**Root Cause**: Portal Backend is slow to respond or unavailable.

**Resolution**:
1. Check Portal Backend health: 
2. Check Portal Backend logs for errors
3. Verify network connectivity between frontend and backend pods
4. Increase timeout in  if needed (currently 30s)

**Validation Evidence**: API calls complete within timeout window, no timeout errors.

### Issue: Form Validation Not Working

**Symptom**: Invalid form data is submitted to backend, backend returns validation errors.

**Root Cause**: Client-side validation is missing or incorrect.

**Resolution**:
1. Add client-side validation for all required fields
2. Add numeric range validation (min/max)
3. Add format validation (e.g., email, URL)
4. Block form submission until validation passes

**Validation Evidence**: Invalid forms are blocked client-side, only valid forms are submitted.

### Issue: Auto-Refresh Not Working

**Symptom**: Metrics page does not auto-refresh, user must manually refresh.

**Root Cause**: Auto-refresh interval not configured or component unmounted.

**Resolution**:
1. Verify  hook is set up correctly with interval
2. Check that component is not unmounting prematurely
3. Verify  state is 

**Validation Evidence**: Metrics update automatically at configured intervals (default: 30s).

## 10. Reproducibility Notes

### What Is Required to Reproduce Portal Frontend Behavior

1. **Node.js 20+**: Runtime for Next.js build and development
2. **npm or yarn**: Package manager
3. **Next.js 15**: Framework (installed via )
4. **Portal Backend**: Must be deployed and accessible
5. **Browser**: Modern browser (Chrome, Firefox, Safari, Edge)

### Build Steps

1. **Install Dependencies**:
   

2. **Configure Environment**:
   - Create  with  (if needed)
   - Or rely on  rewrites

3. **Build**:
   

4. **Run** (development):
   

5. **Run** (production):
   

### Deployment Requirements

1. **Container Image**: Built from 
2. **Kubernetes Cluster**: For containerized deployment
3. **Helm Chart**:  with frontend configuration
4. **Portal Backend**: Must be deployed and accessible at 

### Mocking Strategies

**For Testing Without Portal Backend**:

1. **Mock API Responses**: Use Next.js API routes to mock Portal Backend:
   

2. **Mock Service**: Deploy a simple HTTP server that returns mock responses matching Portal Backend API contract

3. **Development Mode**: Use Next.js rewrites to point to mock backend URL

### Minimal Required Dependencies

- **Next.js 15**: Framework
- **React 18**: UI library
- **Zustand**: State management (optional, can use React Context)
- **Tailwind CSS**: Styling (optional, can use plain CSS)

### Deterministic Behavior Guarantees

- **Form Validation**: Deterministic (same input always validates the same way)
- **API Calls**: Deterministic if Portal Backend responses are deterministic
- **Navigation**: Deterministic (same URL always renders same page)
- **State Management**: Deterministic (Zustand store updates are predictable)

### Known Non-Reproducible Elements

1. **Portal Backend Responses**: Decision outcomes depend on real-time infrastructure state
2. **Network Latency**: API call times vary with network conditions
3. **Browser Behavior**: Different browsers may render slightly differently
4. **User Interactions**: User input and navigation are non-deterministic

### Validation Checklist for Reproduction

- [ ] Frontend builds successfully ()
- [ ] Frontend runs in development mode ()
- [ ] API calls succeed (no CORS errors, no timeouts)
- [ ] Form submission works (template and PLN)
- [ ] Decision results display correctly
- [ ] Metrics page auto-refreshes
- [ ] Error handling works (displays errors to user)
- [ ] Navigation works (all routes accessible)
- [ ] No console errors (except expected API errors)

