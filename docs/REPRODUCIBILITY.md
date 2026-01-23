# TriSLA Reproducibility Guide

## Experimental Version

This documentation corresponds to **TriSLA v3.9.3**, the experimental version used for Chapter 6 results.

## Reproducing Chapter 6 Results

### Required Components

To reproduce the results from Chapter 6, you need:

1. **All Core Services** (Mandatory):
   - SEM-CSMF (v3.9.4)
   - ML-NSMF (v3.9.4)
   - Decision Engine (v3.9.5-fix)
   - BC-NSSMF (v3.9.4)
   - SLA-Agent Layer (v3.9.4)

2. **Infrastructure** (Mandatory):
   - Kafka (message queue)

3. **Network Connectivity**: Services must be able to communicate

### Optional Components

The following components enhance usability but are not required for core functionality:

- Portal Backend/Frontend (v3.8.1)
- UI Dashboard (v3.9.4)
- Traffic Exporter (v3)
- NASP Adapter (v3.9.4) - environment-specific

### Image Versions

**Important**: Use the exact image versions specified in [FROZEN_IMAGES.md](deployment/FROZEN_IMAGES.md):

- Core services: v3.9.4 (except Decision Engine: v3.9.5-fix)
- Portal: v3.8.1
- Traffic Exporter: v3

**Note**: Kafka is currently using  tag. For full reproducibility, this should be fixed to a specific version.

## Known Limitations

### Version Inconsistencies

1. **Decision Engine**: Uses v3.9.5-fix instead of v3.9.4
   - This is a fix version addressing specific issues
   - Results should be reproducible with this version

2. **Portal Components**: Use v3.8.1 (older version)
   - Portal is optional for core functionality
   - Does not affect Chapter 6 results reproduction

3. **Traffic Exporter**: Uses v3 (no patch version)
   - Optional component
   - Does not affect core functionality

### Missing Components

1. **Observability Stack**: Prometheus/Grafana not found in trisla namespace
   - May be deployed in separate namespace
   - Not required for core functionality

2. **Hyperledger Besu**: Not active (Helm release in failed state)
   - Optional component for blockchain features
   - Not required for Chapter 6 results

3. **Zookeeper**: Not present
   - Kafka may be using KRaft mode (no Zookeeper required)

## Reproducibility Checklist

Before claiming reproducibility, verify:

- [ ] All mandatory images pulled successfully
- [ ] All mandatory pods in Running state
- [ ] Decision Engine responds to health checks
- [ ] ML-NSMF can perform inference
- [ ] Kafka is accessible from all services
- [ ] Events are flowing through Kafka
- [ ] Metrics are being collected (if observability enabled)

## Experimental Setup

For Chapter 6 experiments, the following setup was used:

- **Cluster**: NASP
- **Namespace**: trisla
- **Architecture**: TriSLA v3.9.3
- **Registry**: ghcr.io

## Support

For issues with reproducibility, check:

1. [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
2. [FROZEN_IMAGES.md](deployment/FROZEN_IMAGES.md) for image versions
3. [HELM_IMAGE_MAPPING.md](deployment/HELM_IMAGE_MAPPING.md) for configuration
