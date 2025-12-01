FROM otel/opentelemetry-collector:latest

COPY config.yaml /etc/otelcol/config.yaml

EXPOSE 4317 4318 8888 8889

CMD ["--config=/etc/otelcol/config.yaml"]

