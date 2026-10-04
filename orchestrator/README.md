# Orchestrator

Workflow engine that coordinates cross-system SAP operations.

## Components

- engine/ -- Core orchestration: state machine, step execution, compensation
- adapters/ -- System connectors (ABAP Cloud, BTP, SAP HANA, Kyma)
- api/ -- FastAPI REST layer
- models/ -- Pydantic schemas for workflow definitions and events
- tracing/ -- OpenTelemetry integration for distributed tracing

## Design Principles

1. Single entry point -- one API call initiates a multi-system workflow
2. Resilience -- automatic retry with exponential backoff, circuit breaker per system
3. Observability -- trace ID propagated across all hops, structured logging
4. Extensibility -- new system adapters plug in via a standard interface