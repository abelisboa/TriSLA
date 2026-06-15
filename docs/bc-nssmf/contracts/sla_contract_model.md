# SLA Smart Contract Model

> **TRACEABILITY_ONLY — NOT RUNTIME `SLAContract.sol`**
>
> This document describes a simplified research/dissertation struct. The **operational on-chain contract** is `apps/bc-nssmf/src/contracts/SLAContract.sol`. See [`docs/modules/bc-nssmf.md`](../../modules/bc-nssmf.md) for runtime truth.

## Divergence from runtime

| Aspect | This document (research) | Runtime `SLAContract.sol` |
|--------|--------------------------|---------------------------|
| SLA struct | `slaId`, `serviceType`, `decision`, `riskScore`, `timestamp` | `id`, `customer`, `serviceName`, `slaHash`, `status`, `SLO[]`, timestamps |
| SLOs | Not modeled | `SLO { name, value, threshold }` array |
| Status enum | Implicit in `decision` string | `REQUESTED, APPROVED, REJECTED, ACTIVE, COMPLETED` |
| Functions | Conceptual `f(Decision, score, metadata)` | `registerSLA`, `updateSLAStatus`, `getSLA` |

Do **not** use this struct for integration or deployment. Use the Solidity source and `contract_address.json` bundled with BC-NSSMF.

---

## 1. Research SLA representation

```solidity
struct SLA {
    string slaId;
    string serviceType;
    string decision;
    uint256 riskScore;
    uint256 timestamp;
}
```

## 2. Formal interpretation (research)

Decision = decision outcome (ACCEPT / REJECT / RENEGOTIATE)  
score = feasibility score

$$
SLA_{onchain} = f(Decision, score, metadata)
$$

## 3. Guarantee model (research)

Once stored, immutability constraint: $SLA(t) \neq SLA(t+1)$ for committed fields.

## 4. Enforcement (research narrative)

- SLA record cannot be silently altered post-commit
- Violations may be recorded (penalty/compensation contracts — **TRACEABILITY_ONLY**, not in runtime)
- Lifecycle transitions should be valid

**Runtime note:** Only `SLAContract.sol` is **ACTIVE**. Penalty, compensation, and governance registry contracts are **TRACEABILITY_ONLY** — not in the frozen baseline.
