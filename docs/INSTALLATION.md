# Installation (Public Prerequisites)

This document lists the minimum prerequisites for deploying TriSLA.

## Runtime requirements
- Linux host(s) or managed Kubernetes
- Container runtime compatible with Kubernetes (containerd recommended)
- Helm 3

## Network requirements
- Cluster-internal DNS for service discovery
- Optional NodePort or Ingress for Portal exposure

## Container images
TriSLA core images are published under `ghcr.io/abelisboa` with consistent tags.

## Notes
This repository intentionally does not include internal lab evidence packs or sync folders.
