This project builds a complete service monitoring engine using pure Python threading.
It starts with basic health checks, then adds a worker pool, scheduler, metrics aggregator, snapshot persistence, and alerting system.
All monitoring components run as background threads with safe coordination using queues and events.
Finally, a FastAPI interface exposes real-time /metrics and /health endpoints for external dashboards and integrations.
The result is a production-style multi-threaded monitoring agent similar to Datadog/Prometheus node exporters.