# TriSLA Deployment Guide

## Overview

This guide describes how to deploy TriSLA v3.9.3 using Helm charts.

## Prerequisites

Complete the prerequisites from [INSTALLATION.md](INSTALLATION.md) before proceeding.

## Helm Installation

### Install Core TriSLA Services



### Install Portal (Optional)



## Configuration

### Minimum Configuration

The minimum configuration required for deployment:

1. **Registry Authentication**: Ensure cluster can pull from ghcr.io
2. **Namespace**: Create trisla namespace
3. **Image Registry**: Set to ghcr.io/abelisboa

### Custom Values

You can override default values by creating a custom values file:



## Post-Deployment Verification

### Check Pod Status



All mandatory pods should be in  state.

### Verify Services



### Check Logs



### Health Checks

Verify that services are responding:



## Troubleshooting

### Image Pull Errors

If you encounter image pull errors:

1. Verify registry authentication: 
2. Check imagePullSecrets in deployment
3. Verify GITHUB_TOKEN is set and valid

### Pods Not Starting

1. Check pod events: 
2. Check logs: 
3. Verify resource quotas: 

### Kafka Connection Issues

1. Verify Kafka is running: 
2. Check Kafka logs: 
3. Verify service: 

## Next Steps

After successful deployment, see [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for information on reproducing experimental results.
