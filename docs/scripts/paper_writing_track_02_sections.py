# Section bodies for PAPER-WRITING-TRACK-02 (English, reviewer-safe, frozen evidence only).

ABSTRACT = """Network slicing in O-RAN environments requires SLA feasibility to be assessed before resources are committed, yet many orchestration stacks implicitly assume closed-loop causality across admission, core, transport, and lifecycle subsystems. This paper presents TriSLA, a digest-frozen preventive SLA-aware runtime that evaluates feasibility at request time using semantic interpretation, PRB-governed admission scoring, multidomain telemetry snapshots, explainability metadata, detached orchestration, cluster-level reconciliation, and immutable submit-time governance. Under a single pinned container digest (sha256:ca600174…), we report evidence from controlled execution tracks spanning admission (SR, NAD), core attribution (CORE), operational contention (NCM), lifecycle persistence (LIFE), and orchestration feedback boundaries (ORCH). TriSLA demonstrates RAN-dominant hybrid admission with feasibility and resource-headroom awareness (n=450 NASP-hard+ probes), transport-informed scoring without balanced multidomain causality, runtime tri-slice score differentiation under identical network-state identifiers, and persistent NSI/reservation state with periodic reconciliation (10k+ TriSLAReservation CRDs). We further characterize non-causal boundaries: no robust tri-slice admission divergence at frozen guards, no orchestration-to-decision-engine feedback, no core-driven admission under contention campaigns, and no continuous autonomous reevaluation loop. These negative results are positioned as methodological contributions that prevent overclaim and define explicit causal limits for future closed-loop designs."""

INTRODUCTION = """The transition toward software-defined 5G and O-RAN network slicing shifts SLA management from static planning to runtime negotiation. Slice tenants expect service profiles—eMBB, URLLC, and mMTC—to be admitted only when radio, transport, and core resources can sustain contracted KPIs. In practice, admission controllers must therefore operate preventively: they should estimate feasibility before orchestration allocates NSI objects, reserves capacity, or triggers downstream governance actions.

Much of the existing literature emphasizes reactive assurance, simulation-only validation, or architectural diagrams that imply continuous closed-loop control without runtime proof. Orchestration platforms often describe NSI lifecycle management as if reconciliation events automatically recompute admission scores or resource pressure. Similarly, multidomain observability is frequently presented as balanced causal influence across RAN, transport, and core, even when empirical campaigns show dominance of a single domain or snapshot-based decoupling.

TriSLA addresses this gap with a reproducible Kubernetes runtime whose decision semantics, pressure formula, and guard thresholds are frozen under a single digest. The research question guiding this work is: Can SLA feasibility be assessed at request time using runtime multidomain telemetry while preserving explicit causal boundaries between admission, orchestration, reconciliation, lifecycle, and governance? We answer this question substantially—not completely—by proving preventive admission behavior and by formally characterizing paths that do not close the loop.

The contributions of this paper are sixfold. First, we demonstrate preventive SLA-aware admission via score_mode with PRB hard gates under digest-frozen execution. Second, we define and operate a PRB-governed runtime model in which resource pressure is computed from telemetry snapshots at decision time (resource_pressure_v1: 0.4·PRB + 0.3·RTT + 0.3·CPU) rather than from post-orchestration state. Third, we provide semantic persistence through SEM-CSMF SQLite stores for intents, nests, and network slices. Fourth, we implement detached orchestration in which the portal executes NASP instantiation only after decision-engine admission, without callbacks into the decision path. Fifth, we integrate immutable submit-time governance via BC-NSSMF. Sixth, we deliver a cross-track negative characterization of non-causal orchestration, core, lifecycle, and multidomain paths—an explicit scientific outcome rather than an experimental failure.

The remainder of this paper is organized as follows. Section II reviews related work on SLA admission and slicing orchestration. Section III presents the TriSLA architecture and end-to-end workflow. Section IV describes the prototype implementation and runtime scope. Section V explains the evaluation methodology and audit tracks. Section VI reports results and discusses causal boundaries. Section VII states limitations and future work. Section VIII concludes."""

ARCHITECTURE = """This section describes the TriSLA architecture as deployed in our experimental cluster. The design separates intelligence, execution, governance and observability, interfaces, and workflow orchestration. Importantly, admission precedes orchestration, orchestration is detached from decision recomputation, and reconciliation loops update cluster state without feeding the decision engine.

A. Intelligence Layer

The intelligence layer comprises SEM-CSMF, the Decision Engine (DE), and ML-NSMF. SEM-CSMF interprets natural-language or structured SLA intents, persists semantic objects (intents, nests, network slices) in SQLite, and forwards technical metadata to the DE via an internal HTTP evaluate path. The DE computes decision_mode, feasibility, resource pressure, and score_mode outputs using frozen semantics bound to digest sha256:ca600174…. The orchestration_authority and lifecycle_authority modules attach semantic orchestration intent to metadata; they do not execute NASP calls. ML-NSMF supplies risk predictions consumed at decision time when enabled; its outputs inform feasibility coupling but do not constitute post-orchestration feedback.

B. Execution Layer

The execution layer is anchored by the portal backend and NASP adapter. After the DE returns ACCEPT, the portal may invoke POST /api/v1/nsi/instantiate on the NASP adapter with an orchestration payload derived from DE metadata. NASP performs optional 3GPP gate checks, capacity ledger operations, and Kubernetes CRD creation for NetworkSliceInstance and TriSLAReservation objects. A background NSI watch thread and a capacity reconciler (default interval 60 s) expire pending reservations and mark orphaned states when NSI objects disappear. These loops are reconciliatory: they mutate CRD status but do not call the DE or alter pressure formulas.

C. Governance and Observability Layer

BC-NSSMF registers SLA governance lineage on chain at submit time, providing immutable evidence of registration events. The SLA-Agent layer exposes on-demand HTTP ingest and revalidate-telemetry endpoints; under the frozen digest its Kafka consumer loop is not started from main, so continuous autonomous reevaluation is absent. Prometheus-backed telemetry collection in the portal builds multidomain snapshots (RAN, transport, core) used once per submit for pressure and feasibility derivation.

D. Interface Layer

External clients interact through the portal frontend and backend REST API: interpret, submit, status, and revalidate-telemetry. Internal interfaces follow microservice boundaries documented in the interface catalog: SEM intents, DE evaluate (via SEM), NASP instantiate, BC register-sla, and SLA-Agent revalidate. No interface implements NSI→DE or reconciler→DE callbacks.

E. End-to-End Runtime Workflow

The canonical workflow is: (1) semantic interpretation and persistence; (2) preventive admission (score, gates, feasibility, pressure from snapshot); (3) orchestration trigger if ACCEPT; (4) CRD persistence; (5) NSI reconciliation asynchronously; (6) immutable governance registration; (7) optional on-demand SLA-Agent validation. Stages (4)–(5) do not recompute stage (2). This ordering is an architectural invariant validated in ORCH and LIFE tracks."""

PROTOTYPE = """The TriSLA prototype runs on a multi-node Kubernetes cluster (namespace trisla) with digest-pinned images from GHCR. The decision engine image is pinned to sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6 for all reported experiments.

A. Cluster and Core Services

Primary deployments include trisla-portal-backend, trisla-sem-csmf, trisla-decision-engine, trisla-ml-nsmf, trisla-nasp-adapter, trisla-bc-nssmf, trisla-sla-agent-layer, and observability components (Prometheus exporters, OpenTelemetry collector). Service ports follow Helm values: decision engine 8082, NASP adapter 8085, portal backend 8001→container 8888, SEM 8080, BC 8083, SLA-Agent 8084. The experimental 5G core uses free5GC; RAN emulation employs UERANSIM/my5G-RANTester; transport experiments may use ONOS/Mininet paths where configured. Hyperledger Besu supports blockchain registration.

B. Persistence and State Classes

Table I summarizes persistence classes. SEM SQLite holds durable semantic rows. Kubernetes CRDs (TriSLAReservation, NetworkSliceInstance) hold orchestration state with statuses including ACTIVE, ORPHANED, RELEASED, and EXPIRED observed at scale (10,014 reservations; 9,899 NSI objects in freeze snapshots). BC provides immutable submit-time records. DE evidence JSON under /tmp/trisla_evidence is ephemeral per pod. Portal submit responses carry sla_lifecycle metadata but no durable list API (GET /api/v1/sla returns 404).

C. Implemented vs Non-Implemented Scope

Implemented under the frozen digest: preventive admission, portal-driven NASP orchestration, capacity accounting with reconciler, NSI watch, BC register-sla, SLA-Agent HTTP revalidate, transport-informed score terms. Not implemented or not wired: orchestration→DE callbacks, continuous Kafka SLA-Agent loop, unified portal SLA registry, DE execute_slice_creation on the hot path (portal owns instantiate), autonomous closed-loop pressure updates from reconciliation events."""

EVALUATION = """Evaluation follows digest-frozen controlled execution with evidence packs per track. No post-hoc threshold or formula changes were permitted after SSOT baseline lock.

A. Infrastructure and Reproducibility

All tracks reference the same active digest and document kubectl freeze snapshots (deployments, services, pods). Campaign scripts record timestamps, tenant counts, stagger intervals, and guard outcomes. Dataset hashes for SR final freeze are recorded in program metadata.

B. Audit Tracks

SR-EXEC establishes preventive admission and score_mode behavior (n=450 NASP-hard+). NAD-EXEC tests admission boundary engineering and liminal divergence campaigns; robust tri-slice divergence was not validated at the operating points explored. CORE-EXEC measures core/UPF observability and contention; core-driven admission was not observed. NCM-EXEC executes operational orchestration bursts (NCM-ORCH-01: 36 probes, 144 burst submits) measuring HTTP latency and pressure headroom. LIFE-EXEC maps lifecycle persistence, reconciliation, and reevaluation gaps. ORCH-EXEC classifies orchestration causality and detached feedback boundaries.

C. Metrics

Primary metrics include decision score, decision_mode, PRB utilization, resource_pressure, feasibility score, HTTP latency (portal submit path), hard_prb_gate incidence, triplet coherence, admission drift, telemetry snapshot completeness, CRD status distributions, blockchain registration success, and reconciler log activity. Each metric is interpreted with explicit allowed and forbidden claims per track freeze."""

RESULTS = """This section interprets experimental outcomes by metric family, states reviewer-safe claims, and records limitations. Negative results are treated as contributions that bound causal language.

7.1 Preventive Admission and PRB Governance

SR final freeze reports RAN-dominant hybrid admission with PRB hard gates across n=450 NASP-hard+ probes. Score_mode operates with feasibility and resource-headroom awareness under frozen guards. The research question on preventive runtime behavior is substantially answered: admission is computed at request time from telemetry snapshots before orchestration executes.

7.2 Slice-Specific Admission and NAD Boundary Analysis

Score differentiation across eMBB, URLLC, and mMTC is observed under score_mode triplets sharing network_state_id (SR evidence). However, NAD tracks show that robust admission label divergence—especially score_mode-only divergence without path stratification—was not validated at liminal operating points despite higher-stress campaign designs. This negative outcome defines an explicit boundary: slice-aware scoring does not automatically imply slice-aware admission divergence under frozen PRB governance.

7.3 Core Runtime Attribution

CORE-EXEC demonstrates multidomain observability with core/UPF metrics present in telemetry snapshots (pressure_max ≈0.264 in contention probes). Controlled core contention campaigns did not produce admission-causal effects; core behavior is contributive to audit narratives, not a driver of admission recomputation. UPF-first transport paths remain insufficient to establish core dominance.

7.4 Operational Contention and NCM

NCM-ORCH-01 reports mean HTTP submit latency ≈4.49 s and max ≈5.52 s under orchestration burst, versus sub-second baseline—a ratio near 9×. Pressure_max remained ≈0.159 with guards skipping triplets; orchestration contention is therefore operationally observable but not pressure-causal under frozen formulas.

7.5 Lifecycle Persistence and Reconciliation

SEM SQLite retains intents, nests, and slices. NASP maintains 10k+ reservation CRDs with ACTIVE/ORPHANED distributions; reconciler loops run at 60 s intervals. BC persists governance at submit. DE pod evidence is ephemeral. Portal lacks SLA list retrieval; SLA-Agent remains on-demand. NASP reconciliation is continuous; SLA reevaluation is not.

7.6 Orchestration Runtime and Feedback Boundary

ORCH tracks prove admission-before-orchestration ordering and detached orchestration (Portal→NASP→CRD). Code and runtime audits found no NSI→DE callback and no orchestration-driven updates to score, pressure, or feasibility. Orchestration lifecycle metadata appears in submit responses only.

7.7 Causal Boundary Synthesis

Aggregating tracks yields a taxonomy: admission is preventive and observable; core and transport are contributive/observable; orchestration and lifecycle reconciliation are persistent and reconciliatory but detached; multidomain balanced causality and closed-loop orchestration are non-causal under the frozen digest."""

LIMITATIONS = """TriSLA's evaluation exposes structural limitations that should accompany any deployment claim.

No robust tri-slice admission divergence was demonstrated at NAD liminal operating points. Core and orchestration paths do not recompute admission. Orchestration does not feed resource_pressure_v1 or feasibility after instantiate. Lifecycle lacks continuous autonomous reevaluation (Kafka loop unwired). Persistence is fragmented—no unified SLA registry API. Portal GET /api/v1/sla is absent. These limits are invariant under the frozen digest rather than tuning artifacts.

Future work includes orchestration→DE event callbacks, wiring SLA-Agent continuous consumption with durable state, unified lifecycle lineage APIs, session/PDU churn campaigns, explicit core goodness terms, and standards-native interface hardening. Research—not implementation under the current digest—is required to test whether any closed-loop design can remain PRB-governed without violating monotonicity evidence."""

CONCLUSION = """TriSLA demonstrates that SLA feasibility can be assessed preventively at request time under a digest-frozen 5G slicing runtime with PRB-governed admission, semantic persistence, detached orchestration, cluster reconciliation, and immutable submit-time governance. Transport-informed and RAN-dominant behaviors are observable; tri-slice score differentiation under shared network states is reproducible; operational orchestration contention increases HTTP latency without moving frozen pressure targets.

What TriSLA does not prove is equally important for reviewers: no robust admission divergence, no orchestration-driven admission or pressure, no core-driven admission, no continuous autonomous reevaluation, and no balanced multidomain causal closure. These boundaries are empirical outcomes of multi-track audits and should guide both paper claims and future engineering.

The research question is substantially answered with explicit causal limits—an appropriate endpoint for a systems contribution that values reproducibility and negative characterization alongside positive preventive admission evidence."""

DIAGNOSIS = """Sections requiring update from prior TriSLA drafts (per freeze cross-check):

| Section | Issues corrected in this pack |
|---------|------------------------------|
| Abstract | Removed closed-loop/autonomous implications; added negative characterization |
| Introduction | Added explicit RQ, six contributions, causal-boundary gap |
| Architecture | Admission-before-orchestration; detached orch; no DE callback |
| Prototype | Kafka loop unwired; portal 404; digest pinned; scope table |
| Evaluation | Track-based methodology; frozen digest; metric inventory |
| Results | Created §7.1–7.7 with NAD/CORE/NCM/LIFE/ORCH evidence |
| Limitations | Structural limits + future work aligned to LIMIT-PROG-* |
| Conclusion | Replaced placeholder; substantially answered framing |

Removed forbidden expressions: closed-loop causal runtime, autonomous orchestration, orchestration-driven admission, continuous autonomous reevaluation, robust admission divergence, core-driven admission, balanced multidomain causality, normative 3GPP compliance claims."""

FIGURE_REC = """Recommended figure set (IEEE style, event-annotated where applicable):

| Fig | Title | Source track | Replaces decorative charts |
|-----|-------|--------------|---------------------------|
| 1 | TriSLA runtime workflow (preventive→detached→reconcile) | ORCH/Paper | Generic block diagrams without ordering |
| 2 | Final runtime taxonomy heatmap | Consolidation | Unlabeled domain arrows |
| 3 | Decision score vs PRB utilization | SR | — |
| 4 | Admission distribution by decision_mode | SR/NAD | — |
| 5 | Same-state score range by slice (triplets) | SR | — |
| 6 | NCM orchestration latency vs baseline | NCM | — |
| 7 | Lifecycle persistence matrix | LIFE | — |
| 8 | Orchestration feedback absence graph | ORCH | Implied feedback loops |
| 9 | Cross-track convergence map | Consolidation | — |
| 10 | Reviewer-safe claims matrix | Paper writing | — |

NASP analogues: Fig. 6 ↔ NASP Fig. 13 (latency events); Fig. 7 ↔ NASP Fig. 15 (lifecycle resources); persistence before/after ↔ NASP Fig. 14."""

REMOVED_EXPRESSIONS = [
    "fully closed-loop causal runtime",
    "autonomous orchestration",
    "orchestration-driven admission",
    "continuous autonomous reevaluation",
    "multidomain balanced causality",
    "robust tri-slice admission divergence",
    "core-driven admission",
    "continuous validation loop (unqualified)",
    "normative 3GPP/ETSI/O-RAN compliance",
]
