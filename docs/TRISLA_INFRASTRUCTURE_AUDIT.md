# TriSLA Infrastructure Audit Report

## 1. Objective
This document provides a factual audit of the TriSLA experimental environment.

---

## 2. Execution Context

- Access: ssh node006 -> node1
- Working directory: /home/porvir5g/gtp5g/trisla
- Kubernetes environment active

---

## 3. Core Network (5G Core)

### Evidence
- free5GC components detected:
  - AMF, SMF, UPF, NRF, AUSF, PCF, UDM
- Pods in Running state

### Classification
Real 5G Core (3GPP compliant)

---

## 4. Radio Access Network (RAN)

### Evidence
- srsRAN (srsenb)
- UERANSIM (gNB emulator)
- PRB simulator

### Missing
- No Near-RT RIC
- No E2 interface
- No O-RAN metrics

### Classification
Emulated / Hybrid RAN (non O-RAN compliant)

---

## 5. Transport Network

### Evidence
- iperf3 client/server
- traffic-exporter
- network-exporter

### Classification
Real transport network with active measurement

---

## 6. Prometheus Metrics

### Observations
- No E2 or gNB native metrics
- Transport and synthetic metrics available

---

## 7. Final Classification

| Domain     | Status        | Type              |
|------------|---------------|-------------------|
| Core       | Real          | free5GC           |
| Transport  | Real          | iperf-based       |
| RAN        | Emulated      | srsRAN + UERANSIM |

---

## 8. Experimental Environment Definition

The TriSLA architecture is evaluated in a hybrid testbed environment, combining:

- A real 5G Core (free5GC)
- A real transport network with active probing
- An emulated RAN without O-RAN E2 integration

---

## 9. Implications

- RAN metrics must be modeled or emulated
- Core and transport metrics are real
- SLA validation must consider hybrid nature
