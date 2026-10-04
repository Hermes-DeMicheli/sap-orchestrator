# SAP Orchestrator -- Project Notes

## Architecture Overview

SAP Orchestrator coordinates cross-system SAP operations through a
single workflow engine. Each workflow is a sequence of steps, where
each step targets a specific SAP system (ABAP Cloud, BTP, HANA, Kyma).

### Resilience Patterns

- **Circuit breaker per system** -- prevents cascading failures when
  a downstream system is degraded
- **Retry with exponential backoff** -- transient errors handled automatically
- **Compensation** -- on failure, completed steps are reversed in
  reverse order

### Observability

- OpenTelemetry tracing across all adapters
- Structured logging with correlation ID
- Health endpoint for Kubernetes liveness probes

## Key Design Decisions

1. Single entry point API (FastAPI) for all multi-system operations
2. Adapters are swappable -- the engine does not know which system
   it talks to, only the adapter interface contract
3. In-memory state for demo; production uses persistent store
4. Clean Core Level A compliance enforced in ABAP Cloud adapters