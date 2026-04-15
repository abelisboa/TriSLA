## Runbook Reference

This public repository separates:

- structured technical documentation in `docs/`
- internal operational runbooks outside public scope

### Separation policy

- `docs/*` explains architecture, interfaces, runtime behavior, and formal model.
- runbooks execute environment-specific operations (cluster recovery, incident handling, lab procedures).

### Public operational baseline

Use `helm/trisla/README.md` and `docs/reproducibility/setup_guide.md` as the
public operational reference for deploy and validation.
