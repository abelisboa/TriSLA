# NASP Adapter Architecture

## Components

- REST API Layer
- NASP Client
- Metrics Normalization Layer
- Action Executor
- NSI Integration Controller

## Data Flow

TriSLA Modules -> NASP Adapter -> Infrastructure Controllers -> Normalized Response

## Responsibilities

- Abstract infrastructure details from TriSLA core modules
- Normalize domain metrics into a unified model
- Execute platform actions through controlled interfaces

