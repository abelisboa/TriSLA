# Changelog - TriSLA

All notable changes to the TriSLA project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.0] - 2025-01-22

### Added
- Complete repository reorganization with structured documentation
- Comprehensive audit system for validation
- Full NASP deployment preparation
- GHCR image publishing and validation
- Complete interface validation (I-01 to I-07)
- Enhanced security hardening documentation
- Production-ready Helm charts
- Ansible playbooks for NASP deployment

### Changed
- Reorganized all documentation into thematic subdirectories (`docs/api/`, `docs/architecture/`, `docs/deployment/`, etc.)
- Improved `.gitignore` to exclude private content and temporary files
- Updated Helm values for production deployment
- Enhanced docker-compose.yml with health checks and proper dependencies

### Fixed
- Removed all private content from Git versioning
- Cleaned up root directory structure
- Fixed interface configurations
- Resolved dependency issues in modules

### Security
- Removed sensitive files from Git tracking
- Enhanced `.gitignore` rules
- Security hardening documentation added

## [3.3.0] - Previous Release

### Added
- SLA-Agent Layer with autonomous agents
- NASP Adapter integration
- End-to-end validation framework

### Changed
- Decision Engine refactored to use asteval instead of eval()
- BC-NSSMF integrated with real Ethereum permissioned network

## [3.2.0] - Previous Release

### Added
- ML-NSMF with trained models and XAI
- Decision Engine with YAML configuration

### Changed
- SEM-CSMF uses real OWL ontology

## [3.1.0] - Previous Release

### Added
- Initial SEM-CSMF implementation
- Basic infrastructure setup

---

[3.4.0]: https://github.com/abelisboa/TriSLA/releases/tag/v3.4.0

