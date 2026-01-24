# NASP Adapter Complete Guide

This document provides comprehensive technical documentation for the NASP Adapter module, based on the real TriSLA implementation.

## 1. Module Purpose and Design Rationale

### Why NASP Adapter Exists

The NASP Adapter exists to decouple TriSLA from the NASP (Network Automation and Service Platform) implementation details. Without this adapter, every TriSLA module would need direct knowledge of:

- NASP platform service endpoints (srsenb, open5gs UPF/AMF/SMF)
- NASP-specific data formats and protocols
- Network topology and service discovery
- Platform-specific error handling

### Why TriSLA Does Not Talk to NASP Directly

Direct integration would create tight coupling, making TriSLA:

- **Non-portable**: Bound to specific NASP platform versions and topologies
- **Hard to test**: Requiring full NASP infrastructure for unit tests
- **Brittle**: Breaking when NASP services change endpoints or formats
- **Complex**: Spreading NASP knowledge across multiple TriSLA modules

### Decoupling, Portability, and Testability Rationale

The adapter pattern provides:

1. **Abstraction Layer**: Normalizes NASP platform differences behind a stable API
2. **Testability**: Enables mocking NASP responses for unit and integration tests
3. **Portability**: Allows TriSLA to work with different NASP implementations by changing only the adapter
4. **Single Responsibility**: Centralizes all NASP integration logic in one module

## 2. Internal Architecture

### Component Breakdown

The NASP Adapter consists of the following components:



### REST API Layer

The FastAPI application () exposes four endpoints:

- : Health check
- : Metrics collection
- : Action execution
- : NSI creation

### NASP Client Abstraction

The  class () abstracts HTTP communication with NASP platform services:

- **RAN Domain**: Queries  (metrics) and  (actions)
- **Transport Domain**: Queries 
- **Core Domain**: Queries  (UPF metrics),  (AMF),  (SMF)

### Error Mapping Layer

Errors from NASP platform are caught and normalized:

- HTTP timeouts → Return error dict with domain context
- Connection failures → Logged with OpenTelemetry spans
- Invalid responses → Wrapped in error payloads

### Timeout and Retry Strategy

- **HTTP Client Timeout**: 30 seconds (configured in )
- **Metrics Query Timeout**: 10 seconds per domain
- **No Automatic Retries**: Failures are returned to caller for handling
- **Fallback Behavior**: For RAN and Core metrics, attempts primary endpoint, then fallback endpoint

### NSI Watch Controller

A daemon thread () monitors Network Slice Instances via Kubernetes watch API:

- Watches  CRDs in the default namespace
- On , creates Kubernetes resources:
  - Namespace (if URLLC profile)
  - ResourceQuota (if URLLC profile)
  - NetworkPolicy (allow-all ingress/egress)
- Updates NSI status based on resource creation outcomes

## 3. Supported Operations

### Resource Availability Query

**Purpose**: Retrieve real-time infrastructure metrics from NASP platform domains.

**Triggering Module**: SLA-Agent, Decision Engine, BC-NSSMF (via HTTP GET)

**Input Payload**: None (query parameters optional)

**Output Payload**:


**Failure Behavior**: Returns error dict per domain:


### Metrics Retrieval

**Purpose**: Aggregate metrics from all NASP domains (RAN, Transport, Core).

**Triggering Module**: SLA-Agent (periodic), Decision Engine (on-demand)

**Input Payload**: None

**Output Payload**: Same as Resource Availability Query (aggregated)

**Failure Behavior**: Partial results with error dicts for failed domains

### Slice Activation Request

**Purpose**: Execute control-plane action to activate a network slice in the RAN domain.

**Triggering Module**: SLA-Agent (after ACCEPT decision)

**Input Payload**:


**Output Payload**:


**Failure Behavior**: Raises exception, caught by ActionExecutor, returned as error response

### Network Slice Instance (NSI) Instantiation

**Purpose**: Create a Network Slice Instance as a Kubernetes Custom Resource.

**Triggering Module**: SLA-Agent, Portal Backend

**Input Payload**:


**Output Payload**:


**Failure Behavior**: Returns error response:


### Monitoring Hook Setup

**Purpose**: NSI Watch Controller automatically sets up monitoring when NSI phase transitions to .

**Triggering Module**: NSIWatchController (daemon thread)

**Input**: NSI CRD with 

**Output**: Kubernetes resources created (Namespace, ResourceQuota, NetworkPolicy)

**Failure Behavior**: Logged, NSI status updated with error message

## 4. REST API Specification

### Endpoints

#### GET /health

**Description**: Health check endpoint

**Response**:


**Status Codes**:
- : Service is healthy

#### GET /api/v1/nasp/metrics

**Description**: Retrieve normalized platform metrics from all NASP domains

**Query Parameters**: None

**Response**:


**Status Codes**:
- : Metrics retrieved (may contain partial errors per domain)

#### POST /api/v1/nasp/actions

**Description**: Execute a platform action

**Request Body**:


**Response**:


**Status Codes**:
- : Action executed successfully
- : Invalid action payload
- : Action execution failed

#### POST /api/v1/nsi/instantiate

**Description**: Create a Network Slice Instance

**Request Body**:


**Response**:


**Status Codes**:
- : NSI created successfully
- : Invalid NSI specification
- : NSI creation failed

### Error Responses

All endpoints return error responses in the format:


## 5. Execution Flow (Step-by-Step)

### Example: Metrics Collection Request

1. **SLA-Agent** sends HTTP GET request to 

2. **FastAPI** routes request to  handler in 

3. **OpenTelemetry** creates span 

4. **MetricsCollector.collect_all()** is invoked:
   - Initializes result dict with , , , , 
   - Calls :
     - HTTP GET to  (timeout 10s)
     - On failure, fallback to 
     - Returns metrics or error dict
   - Calls :
     - HTTP GET to  (timeout 10s)
     - Returns metrics or error dict
   - Calls :
     - HTTP GET to  (timeout 10s)
     - On failure, fallback to 
     - Returns metrics or error dict
   - Aggregates all results into single dict

5. **OpenTelemetry** sets span attributes:
   - 
   - 
   - 
   - 

6. **FastAPI** returns aggregated metrics dict as JSON response

7. **SLA-Agent** receives response and processes metrics

### Example: NSI Instantiation Request

1. **SLA-Agent** sends HTTP POST to  with NSI spec

2. **FastAPI** routes to  handler

3. **OpenTelemetry** creates span 

4. **NSIController.create_nsi()** is invoked:
   - Generates NSI ID if not provided: 
   - Constructs NSI CRD body:
     - 
     - 
     - 
     - 
     -  include , , 
     -  contains , , , , 
     - 
   - Calls :
     - Group: 
     - Version: 
     - Plural: 
     - Namespace: 
     - Body: NSI CRD

5. **Kubernetes API** creates NSI CRD

6. **NSIWatchController** (daemon thread) detects new NSI via watch API

7. **NSIWatchController** waits for 

8. **NSIWatchController** creates Kubernetes resources:
   - Namespace (if )
   - ResourceQuota (if )
   - NetworkPolicy (allow-all)

9. **NSIWatchController** updates NSI status with resource creation results

10. **FastAPI** returns success response with created NSI

## 6. Integration with Other TriSLA Modules

### SLA-Agent

**Call Direction**: SLA-Agent → NASP Adapter

**Data Exchanged**:
- **Request**: HTTP GET  (periodic or on-demand)
- **Request**: HTTP POST  (action execution)
- **Request**: HTTP POST  (NSI creation)
- **Response**: Normalized metrics or action results

**Responsibility Boundary**:
- **SLA-Agent**: Orchestrates SLA lifecycle, decides when to query metrics or execute actions
- **NASP Adapter**: Executes queries/actions, normalizes responses

**Integration Points**:
- SLA-Agent imports  from  package (if available in PYTHONPATH)
- Otherwise, SLA-Agent uses HTTP client to call NASP Adapter REST API
- Service discovery:  (configured in Helm values)

### Decision Engine

**Call Direction**: Decision Engine → NASP Adapter (indirect, via SLA-Agent or direct HTTP)

**Data Exchanged**:
- **Request**: HTTP GET  (for infrastructure signals)
- **Response**: Normalized metrics used in decision logic

**Responsibility Boundary**:
- **Decision Engine**: Uses metrics as input to admission decisions
- **NASP Adapter**: Provides metrics, does not interpret them

**Integration Points**:
- Decision Engine may query NASP Adapter directly for real-time metrics
- Or Decision Engine receives metrics via SLA-Agent aggregation

### Observability Stack

**Call Direction**: NASP Adapter → Observability Stack

**Data Exchanged**:
- **OpenTelemetry Spans**: Created for all NASP platform calls
  - Span names: , , , , , 
  - Attributes: , , , , , 
- **Prometheus Metrics**: Exposed via FastAPI instrumentation (if enabled)
- **Logs**: Structured logging for all operations

**Responsibility Boundary**:
- **NASP Adapter**: Emits observability signals
- **Observability Stack**: Collects, stores, and visualizes signals

**Integration Points**:
- OpenTelemetry: OTLP endpoint configured via  and  environment variables
- Prometheus: Scrapes FastAPI metrics endpoint (if instrumentation enabled)

## 7. Deployment and Configuration

### Helm Configuration

The NASP Adapter is deployed as part of the TriSLA Helm chart. Configuration is provided in :



### Required Environment Variables

- **NASP_MODE**:  (production) or  (development). Default: 

**For Real Mode (Production)**:
- **NASP_RAN_ENDPOINT**: RAN service endpoint. Default: 
- **NASP_RAN_METRICS_ENDPOINT**: RAN metrics endpoint. Default: 
- **NASP_CORE_UPF_ENDPOINT**: Core UPF endpoint. Default: 
- **NASP_CORE_UPF_METRICS_ENDPOINT**: Core UPF metrics endpoint. Default: 
- **NASP_CORE_AMF_ENDPOINT**: Core AMF endpoint. Default: 
- **NASP_CORE_SMF_ENDPOINT**: Core SMF endpoint. Default: 
- **NASP_TRANSPORT_ENDPOINT**: Transport endpoint. Default: 
- **NASP_CORE_ENDPOINT**: Core endpoint (fallback). Default: 

**For Mock Mode (Development)**:
- **NASP_RAN_ENDPOINT**: Mock RAN endpoint. Default: 
- **NASP_TRANSPORT_ENDPOINT**: Mock transport endpoint. Default: 
- **NASP_CORE_ENDPOINT**: Mock core endpoint. Default: 

**Optional**:
- **OTLP_ENABLED**: Enable OpenTelemetry. Default: 
- **OTLP_ENDPOINT**: OTLP collector endpoint. Default: 
- **TRISLA_TENANT_ID**: Tenant ID for NSI creation. Default: 

### Example Helm Values Snippet



### Kubernetes RBAC

The NASP Adapter requires RBAC permissions to:
- Create/read/update  CRDs
- Create/read namespaces
- Create/read ResourceQuotas
- Create/read NetworkPolicies

RBAC is configured in .

## 8. Observability and Evidence

### Prometheus Metrics

The NASP Adapter exposes metrics via FastAPI instrumentation (if enabled):

- **Request Count**: Total HTTP requests received
- **Request Latency**: Histogram of request processing time
- **Metrics Collection Count**: Counter for metrics collection operations
- **Action Execution Count**: Counter for action executions

### OpenTelemetry Traces

Spans are created for all NASP platform interactions:

**Span Names**:
-  (metrics collection endpoint)
-  (action execution endpoint)
-  (NSI creation endpoint)
-  (RAN metrics query)
-  (transport metrics query)
-  (core metrics query)
-  (NSI CRD creation)
-  (connection check)

**Span Attributes**:
- :  or 
- : Endpoint URL queried
- : Comma-separated list of domains queried
- : Domain of action (, , )
- : Type of action (, etc.)
- : Boolean indicating execution success
- : NSI identifier
- : NSI lifecycle phase

**Trace Context**: Spans are linked to parent spans from calling modules (SLA-Agent, Decision Engine) via trace context propagation.

### Log Structure

Structured logging is used throughout:

**Metrics Collection**:


**Action Execution**:


**NSI Lifecycle**:


### How to Verify Adapter Correctness at Runtime

1. **Health Check**:
   
   Expected: 

2. **Metrics Collection**:
   
   Expected: JSON with , ,  keys (may contain error dicts for failed domains)

3. **OpenTelemetry Traces**:
   - Query OTLP collector for spans with 
   - Verify spans are created for all NASP platform calls
   - Check span attributes match expected values

4. **Kubernetes Resources**:
   

5. **Logs**:
   
   Verify no repeated errors, successful metrics collection, NSI watch controller running

## 9. Failure Modes and Resolved Issues

### Issue: NASP Platform Unreachable

**Symptom**: Metrics collection returns empty or error dicts for all domains. Health check shows .

**Root Cause**: Network connectivity issues, incorrect endpoint URLs, or NASP services not running.

**Resolution**:
1. Verify NASP service endpoints are correct in environment variables
2. Check network policies allow traffic from NASP Adapter pod to NASP services
3. Verify NASP services are running: , 
4. Test connectivity from NASP Adapter pod: 

**Validation Evidence**: Metrics collection returns valid data, health check shows .

### Issue: Timeout Errors

**Symptom**: HTTP requests to NASP platform timeout after 10 seconds. Logs show .

**Root Cause**: NASP services are slow to respond, network latency, or service overload.

**Resolution**:
1. Increase HTTP client timeout in  (currently 30s for client, 10s per request)
2. Verify NASP service health and resource availability
3. Check network latency between NASP Adapter and NASP services

**Validation Evidence**: Requests complete within timeout window, no timeout exceptions in logs.

### Issue: Partial Data Returned

**Symptom**: Metrics collection returns data for some domains but error dicts for others (e.g.,  succeeds,  fails).

**Root Cause**: Individual NASP service failures, network partitions, or endpoint misconfiguration.

**Resolution**:
1. Check error dicts in response to identify failing domains
2. Verify endpoint URLs for failing domains
3. Test connectivity to specific failing endpoints
4. NASP Adapter continues to return partial results (graceful degradation)

**Validation Evidence**: All domains return valid metrics, or error dicts are properly formatted with error messages.

### Issue: Invalid Responses from NASP Platform

**Symptom**: NASP platform returns non-JSON responses or malformed JSON. Metrics collection fails with parsing errors.

**Root Cause**: NASP service returns HTML error pages, plain text, or invalid JSON.

**Resolution**:
1. NASP Adapter checks  header before parsing JSON
2. Falls back to  if content is not JSON
3. Logs response content for debugging

**Validation Evidence**: Metrics collection handles non-JSON responses gracefully, returns  dict.

### Issue: NSI Creation Fails with ApiException

**Symptom**:  returns  with  message.

**Root Cause**: Kubernetes API server unreachable, RBAC permissions missing, or CRD not installed.

**Resolution**:
1. Verify NASP Adapter ServiceAccount has required RBAC permissions (check )
2. Verify  CRD is installed: 
3. Check Kubernetes API server connectivity from NASP Adapter pod
4. Verify  in deployment

**Validation Evidence**: NSI creation succeeds, NSI CRD appears in Kubernetes, NSI watch controller detects it.

### Issue: NSI Watch Controller Not Starting

**Symptom**: NSI Watch Controller daemon thread dies immediately after startup. Logs show .

**Root Cause**: Kubernetes client initialization failure, missing ServiceAccount token, or invalid cluster configuration.

**Resolution**:
1. Verify ServiceAccount exists and has correct RBAC permissions
2. Check  in deployment
3. Verify in-cluster config is valid: 
4. Check logs for specific Kubernetes client initialization errors

**Validation Evidence**: NSI Watch Controller thread stays alive, logs show successful watch initialization, NSI phase transitions trigger resource creation.

## 10. Reproducibility Notes

### What Is Required to Reproduce NASP Adapter Behavior

1. **Kubernetes Cluster**: Single-node or multi-node cluster with:
   - Service discovery (DNS for )
   - RBAC enabled
   - Custom Resource Definitions (CRDs) support

2. **NASP Platform Services**: Real or mock NASP services:
   - **RAN**: srsenb service (or mock) at  (metrics) and  (actions)
   - **Transport**: open5gs UPF service (or mock) at 
   - **Core**: open5gs UPF (metrics at ), AMF at , SMF at 

3. **TriSLA Dependencies**:
   - Helm 3
   - TriSLA Helm chart with 
   - NetworkSliceInstance CRD installed

4. **Observability (Optional)**:
   - OpenTelemetry collector (if )
   - Prometheus (for metrics scraping)

### Mocking Strategies

For testing without real NASP platform:

1. **Set **: Uses mock endpoints (, etc.)
2. **Deploy Mock Services**: Deploy simple HTTP servers that return JSON responses matching expected NASP formats
3. **Mock NASPClient**: In unit tests, mock  class to return predefined responses

### Minimal NASP Interface Assumptions

The NASP Adapter assumes NASP platform services expose:

1. **Metrics Endpoint**:  returns JSON or text metrics
2. **Action Endpoint** (RAN only):  accepts action payload, returns result
3. **HTTP/HTTPS Protocol**: Standard HTTP with JSON content type
4. **Timeout Tolerance**: Services respond within 10 seconds

### Deterministic Behavior Guarantees

- **Metrics Collection**: Results are deterministic if NASP platform state is stable (same queries return same results)
- **Action Execution**: Results depend on NASP platform state (non-deterministic if platform state changes)
- **NSI Creation**: Deterministic (Kubernetes API is consistent)
- **NSI Watch**: Non-deterministic timing (depends on Kubernetes watch API events)

### Known Non-Reproducible Elements

1. **NASP Platform State**: Metrics values depend on real-time platform state (CPU, memory, network)
2. **Network Latency**: HTTP request/response times vary with network conditions
3. **Kubernetes Watch Events**: Timing of NSI phase transitions depends on external controllers
4. **Error Conditions**: Some failures (timeouts, connection errors) are non-deterministic

### Validation Checklist for Reproduction

- [ ] NASP Adapter pod is Running
- [ ] Health endpoint returns 
- [ ] Metrics endpoint returns data for at least one domain
- [ ] NSI creation succeeds and CRD appears in Kubernetes
- [ ] NSI Watch Controller creates resources when NSI phase = Accepted
- [ ] OpenTelemetry spans are created (if OTLP enabled)
- [ ] No repeated errors in logs
