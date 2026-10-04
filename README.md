# SAP Orchestrator

Multi-system orchestration framework for SAP ecosystems. Coordinates ABAP Cloud, BTP services, and SAP HANA through a single workflow engine with retry, circuit breaker, and distributed tracing.

## Stack

- Python/FastAPI -- workflow engine, REST API, adapters
- ABAP Cloud -- business logic executor (RAP, clean ABAP)
- CAP/UI5 -- service bindings, OData, frontend
- BTP/Kyma -- event mesh, secrets, deployment

## Structure

- orchestrator/ -- Python FastAPI workflow engine
- abap-cloud/ -- ABAP Cloud executors and behavior definitions
- cap-services/ -- CAP CDS models and service bindings
- btp-integration/ -- BTP service connectors and Kyma configs
- docs/ -- architecture and study notes

## Quick Start

```bash
cd orchestrator
pip install -e .
uvicorn src.orchestrator.main:app --reload
```