# Portal Frontend Navigation Hub

This README is a navigation hub for Portal Frontend documentation. It is not the
operational SSOT. The canonical operational module reference is:

```text
docs/modules/portal-frontend.md
```

## Runtime Identity

Portal Frontend is the user interface and workflow visualization layer. It
presents decisions, governance evidence, runtime state, telemetry views, and
observability data returned through Portal Backend.

Portal Frontend does not decide SLA, does not produce governance, does not
produce runtime assurance, does not produce explainability, and does not produce
telemetry.

## Direct Integration

```text
Frontend
|
Portal Backend
```

Portal Frontend does not directly call SEM-CSMF, Decision Engine, BC-NSSMF, or
SLA-Agent.

## Main Navigation

```text
/
/pnl
/template
/sla-lifecycle?view=admission
/sla-lifecycle?view=runtime
/monitoring
/administration
```

Auxiliary route:

```text
/metrics
```

Reserved active route outside the main menu and not hot path:

```text
/defense
```

## Runtime Stack

Active runtime stack: Next.js 15 App Router, React 18, React Context, and
`sessionStorage` for the admission operational snapshot cache.

Zustand is not implemented in the current runtime.

## References

- Canonical module document: `docs/modules/portal-frontend.md`
- Portal Backend module: `docs/modules/portal-backend.md`
- Observability module: `docs/modules/observability.md`
- Telemetry module: `docs/modules/telemetry.md`
- Architecture reference: `docs/portal/architecture/portal_architecture.md`
