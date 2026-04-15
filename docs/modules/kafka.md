# Kafka

## Role as Event Bus

Kafka acts as the asynchronous event backbone for TriSLA where enabled. It
supports decoupled communication between producers and consumers in prediction,
decision, and lifecycle paths.

## Integration with Modules

Kafka is used by multiple services (depending on runtime configuration), such as:

- ML prediction publication/consumption paths;
- decision event propagation;
- SLA-Agent event ingestion/publication channels.

## Message Flow

Typical flow is producer -> topic -> consumer, allowing modules to exchange
events without tight request-response coupling. This improves resilience and
supports scalable pipeline behavior under variable load.
