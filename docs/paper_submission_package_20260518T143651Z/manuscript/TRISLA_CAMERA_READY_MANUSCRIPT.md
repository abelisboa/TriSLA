% TriSLA Camera-Ready Manuscript (IEEEtran-compatible Markdown export)

% Active digest: sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6

% Generated: 2026-05-18T14:25:49.125829+00:00



# TriSLA: A Tri-Dimensional SLA-Aware Orchestration Architecture for O-RAN Networks with Explainable AI and Blockchain Compliance



## Abstract

Network slicing in O-RAN environments requires SLA feasibility to be assessed before resources are committed, yet many orchestration stacks implicitly assume closed-loop causality across admission, core, transport, and lifecycle subsystems. This paper presents TriSLA, a digest-frozen preventive SLA-aware runtime that evaluates feasibility at request time using semantic interpretation, PRB-governed admission scoring, multidomain telemetry snapshots, explainability metadata, detached orchestration, cluster-level reconciliation, and immutable submit-time governance. Under a single pinned container digest (sha256:ca600174…), we report evidence from controlled execution tracks spanning admission (SR, NAD), core attribution (CORE), operational contention (NCM), lifecycle persistence (LIFE), and orchestration feedback boundaries (ORCH). TriSLA demonstrates RAN-dominant hybrid admission with feasibility and resource-headroom awareness (n=450 NASP-hard+ probes), transport-informed scoring without balanced multidomain causality, runtime tri-slice score differentiation under identical network-state identifiers, and persistent NSI/reservation state with periodic reconciliation (10k+ TriSLAReservation CRDs). We further characterize non-causal boundaries: no robust tri-slice admission divergence at frozen guards, no orchestration-to-decision-engine feedback, no core-driven admission under contention campaigns, and no continuous autonomous reevaluation loop. These negative results are positioned as methodological contributions that prevent overclaim and define explicit causal limits for future closed-loop designs.



## I. Introduction

The transition toward software-defined 5G and O-RAN network slicing shifts SLA management from static planning to runtime negotiation. Slice tenants expect service profiles—eMBB, URLLC, and mMTC—to be admitted only when radio, transport, and core resources can sustain contracted KPIs. In practice, admission controllers must therefore operate preventively: they should estimate feasibility before orchestration allocates NSI objects, reserves capacity, or triggers downstream governance actions.

Much of the existing literature emphasizes reactive assurance, simulation-only validation, or architectural diagrams that imply continuous closed-loop control without runtime proof. Orchestration platforms often describe NSI lifecycle management as if reconciliation events automatically recompute admission scores or resource pressure. Similarly, multidomain observability is frequently presented as balanced causal influence across RAN, transport, and core, even when empirical campaigns show dominance of a single domain or snapshot-based decoupling.

TriSLA addresses this gap with a reproducible Kubernetes runtime whose decision semantics, pressure formula, and guard thresholds are frozen under a single digest. The research question guiding this work is: Can SLA feasibility be assessed at request time using runtime multidomain telemetry while preserving explicit causal boundaries between admission, orchestration, reconciliation, lifecycle, and governance? We answer this question substantially—not completely—by proving preventive admission behavior and by formally characterizing paths that do not close the loop.

The contributions of this paper are sixfold. First, we demonstrate preventive SLA-aware admission via score_mode with PRB hard gates under digest-frozen execution. Second, we define and operate a PRB-governed runtime model in which resource pressure is computed from telemetry snapshots at decision time (resource_pressure_v1: 0.4·PRB + 0.3·RTT + 0.3·CPU) rather than from post-orchestration state. Third, we provide semantic persistence through SEM-CSMF SQLite stores for intents, nests, and network slices. Fourth, we implement detached orchestration in which the portal executes NASP instantiation only after decision-engine admission, without callbacks into the decision path. Fifth, we integrate immutable submit-time governance via BC-NSSMF. Sixth, we deliver a cross-track negative characterization of non-causal orchestration, core, lifecycle, and multidomain paths—an explicit scientific outcome rather than an experimental failure.

The remainder of this paper is organized as follows. Section II reviews related work on SLA admission and slicing orchestration. Section III presents the TriSLA architecture and end-to-end workflow. Section IV describes the prototype implementation and runtime scope. Section V explains the evaluation methodology and audit tracks. Section VI reports results and discusses causal boundaries. Section VII states limitations and future work. Section VIII concludes.



## II. Related Work

Network slicing has been studied extensively from architectural, orchestration, and admission-control perspectives. Surveys on 5G slicing emphasize SDN/NFV enablement, end-to-end resource isolation, and the tension between tenant-specific QoS and shared infrastructure efficiency~\cite{Afolabi2018SlicingSurvey,OrdonezLucena2017Slicing,Foukas2017Survey,Li2021E2E}. O-RAN introduces open interfaces and programmatic RAN control, yet operational platforms still require application-level admission logic that remains auditable under real deployments~\cite{Polese2022ORAN,oran_open_smart_ran,oran-survey-2023}. SLA-aware service chaining and admission frameworks address feasibility at provisioning time~\cite{Orfanos2020SFC,Sun2022SLAAdmission,Bega2021Admission,Xu2020AIAdmission}, while AI-assisted orchestration proposals often assume multidomain feedback without publishing negative paths when feedback is absent~\cite{ahmad2023ai,sharma2022aiempowered,ai-orch-2023}.

Explainable decision support and semantic intent modeling appear in parallel lines of work~\cite{Guidotti2018XAI,xai-survey,Gruber1993,Studer1998}. Blockchain-based SLA management targets immutable contracting~\cite{Zhang2020Blockchain,Ferreira2022BlockchainSLA,Javed2024Review,bao2022blockchain,choi2023slaver}, and standards bodies define reference architectures for slice management~\cite{3GPP2020NRM,3gpp28541,ETSI2021ZSM,gsma_ng116}. Platform-oriented studies such as NASP integrate 3GPP, ETSI, and O-RAN constructs in a Network-Slice-as-a-Service workflow with detailed runtime evaluation~\cite{grings2025nasp}; TriSLA differs by foregrounding preventive admission under a digest-frozen decision plane and by reporting explicit non-causal boundaries for orchestration, core, and lifecycle subsystems.

TriSLA therefore positions itself as a reproducible runtime with PRB-governed preventive admission, detached orchestration, reconciliatory cluster state, and a documented set of limits that prior slice-management papers often omit—without claiming autonomous feedback closure across admission and orchestration.



## III. TriSLA Architecture

This section describes the TriSLA architecture as deployed in our experimental cluster. The design separates intelligence, execution, governance and observability, interfaces, and workflow orchestration. Importantly, admission precedes orchestration, orchestration is detached from decision recomputation, and reconciliation loops update cluster state without feeding the decision engine.

A. Intelligence Layer

The intelligence layer comprises SEM-CSMF, the Decision Engine (DE), and ML-NSMF. SEM-CSMF interprets natural-language or structured SLA intents, persists semantic objects (intents, nests, network slices) in SQLite, and forwards technical metadata to the DE via an internal HTTP evaluate path. The DE computes decision_mode, feasibility, resource pressure, and score_mode outputs using frozen semantics bound to digest sha256:ca600174…. The orchestration_authority and lifecycle_authority modules attach semantic orchestration intent to metadata; they do not execute NASP calls. ML-NSMF supplies risk predictions consumed at decision time when enabled; its outputs inform feasibility coupling but do not constitute post-orchestration feedback.

B. Execution Layer

The execution layer is anchored by the portal backend and NASP adapter. After the DE returns ACCEPT, the portal may invoke POST /api/v1/nsi/instantiate on the NASP adapter with an orchestration payload derived from DE metadata. NASP performs optional 3GPP gate checks, capacity ledger operations, and Kubernetes CRD creation for NetworkSliceInstance and TriSLAReservation objects. A background NSI watch thread and a capacity reconciler (default interval 60 s) expire pending reservations and mark orphaned states when NSI objects disappear. These loops are reconciliatory: they mutate CRD status but do not call the DE or alter pressure formulas.

C. Governance and Observability Layer

BC-NSSMF registers SLA governance lineage on chain at submit time, providing immutable evidence of registration events. The SLA-Agent layer exposes on-demand HTTP ingest and revalidate-telemetry endpoints; under the frozen digest its Kafka consumer loop is not started from main, so continuous autonomous reevaluation is absent. Prometheus-backed telemetry collection in the portal builds multidomain snapshots (RAN, transport, core) used once per submit for pressure and feasibility derivation.

D. Interface Layer

External clients interact through the portal frontend and backend REST API: interpret, submit, status, and revalidate-telemetry. Internal interfaces follow microservice boundaries documented in the interface catalog: SEM intents, DE evaluate (via SEM), NASP instantiate, BC register-sla, and SLA-Agent revalidate. No interface implements NSI→DE or reconciler→DE callbacks.

E. End-to-End Runtime Workflow

The canonical workflow is: (1) semantic interpretation and persistence; (2) preventive admission (score, gates, feasibility, pressure from snapshot); (3) orchestration trigger if ACCEPT; (4) CRD persistence; (5) NSI reconciliation asynchronously; (6) immutable governance registration; (7) optional on-demand SLA-Agent validation. Stages (4)–(5) do not recompute stage (2). This ordering is an architectural invariant validated in ORCH and LIFE tracks.



## IV. Prototype Implementation

The TriSLA prototype runs on a multi-node Kubernetes cluster (namespace trisla) with digest-pinned images from GHCR. The decision engine image is pinned to sha256:ca60017448ab18d469ac5c9be4d9ccdb78c02c844b16e16463dd09e91ae9b6b6 for all reported experiments.

A. Cluster and Core Services

Primary deployments include trisla-portal-backend, trisla-sem-csmf, trisla-decision-engine, trisla-ml-nsmf, trisla-nasp-adapter, trisla-bc-nssmf, trisla-sla-agent-layer, and observability components (Prometheus exporters, OpenTelemetry collector). Service ports follow Helm values: decision engine 8082, NASP adapter 8085, portal backend 8001→container 8888, SEM 8080, BC 8083, SLA-Agent 8084. The experimental 5G core uses free5GC; RAN emulation employs UERANSIM/my5G-RANTester; transport experiments may use ONOS/Mininet paths where configured. Hyperledger Besu supports blockchain registration.

B. Persistence and State Classes

Table I summarizes persistence classes. SEM SQLite holds durable semantic rows. Kubernetes CRDs (TriSLAReservation, NetworkSliceInstance) hold orchestration state with statuses including ACTIVE, ORPHANED, RELEASED, and EXPIRED observed at scale (10,014 reservations; 9,899 NSI objects in freeze snapshots). BC provides immutable submit-time records. DE evidence JSON under /tmp/trisla_evidence is ephemeral per pod. Portal submit responses carry sla_lifecycle metadata but no durable list API (GET /api/v1/sla returns 404).

C. Implemented vs Non-Implemented Scope

Implemented under the frozen digest: preventive admission, portal-driven NASP orchestration, capacity accounting with reconciler, NSI watch, BC register-sla, SLA-Agent HTTP revalidate, transport-informed score terms. Not implemented or not wired: orchestration→DE callbacks, continuous Kafka SLA-Agent loop, unified portal SLA registry, DE execute_slice_creation on the hot path (portal owns instantiate), autonomous closed-loop pressure updates from reconciliation events.



## V. Experimental Methodology

Evaluation follows digest-frozen controlled execution with evidence packs per track. No post-hoc threshold or formula changes were permitted after SSOT baseline lock.

A. Infrastructure and Reproducibility

All tracks reference the same active digest and document kubectl freeze snapshots (deployments, services, pods). Campaign scripts record timestamps, tenant counts, stagger intervals, and guard outcomes. Dataset hashes for SR final freeze are recorded in program metadata.

B. Audit Tracks

SR-EXEC establishes preventive admission and score_mode behavior (n=450 NASP-hard+). NAD-EXEC tests admission boundary engineering and liminal divergence campaigns; robust tri-slice divergence was not validated at the operating points explored. CORE-EXEC measures core/UPF observability and contention; core-driven admission was not observed. NCM-EXEC executes operational orchestration bursts (NCM-ORCH-01: 36 probes, 144 burst submits) measuring HTTP latency and pressure headroom. LIFE-EXEC maps lifecycle persistence, reconciliation, and reevaluation gaps. ORCH-EXEC classifies orchestration causality and detached feedback boundaries.

C. Metrics

Primary metrics include decision score, decision_mode, PRB utilization, resource_pressure, feasibility score, HTTP latency (portal submit path), hard_prb_gate incidence, triplet coherence, admission drift, telemetry snapshot completeness, CRD status distributions, blockchain registration success, and reconciler log activity. Each metric is interpreted with explicit allowed and forbidden claims per track freeze.



## VI. Results and Discussion

This section reports experimental outcomes organized by metric family. Each subsection states the evaluation objective, summarizes frozen campaign evidence, interprets operational behavior, and records reviewer-safe claims together with explicit limits. Negative outcomes are treated as methodological contributions.

\subsection{Preventive Admission}
The SR final freeze evaluates whether TriSLA performs SLA-aware admission at request time under pinned images (digest \texttt{ca600174…}). Across $n{=}450$ NASP-hard+ probes, score\_mode operates with PRB hard gates, feasibility coupling, and resource-headroom awareness. The research question on preventive runtime behavior is \emph{substantially answered}: admission is computed from multidomain telemetry snapshots before orchestration executes. We do not claim that every slice class exhibits distinct admission labels under identical network-state identifiers without stratification (see Section~VI-D).

\subsection{PRB Governance}
Resource pressure follows the frozen composite $\text{resource\_pressure\_v1} = 0.4\cdot\text{PRB} + 0.3\cdot\text{RTT} + 0.3\cdot\text{CPU}$, evaluated at decision time from the portal-collected telemetry snapshot. PRB utilization therefore dominates the pressure narrative in line with RAN-dominant hybrid admission evidence, while transport and core terms remain observable contributors. Post-orchestration CRD state does not re-enter the pressure formula (ORCH freeze).

\subsection{Slice-Aware Behavior}
Score\_mode produces runtime tri-slice score differentiation under the same \texttt{network\_state\_id} in controlled triplets (SR evidence). This supports slice-aware \emph{scoring} under shared radio conditions. Admission-label divergence across slices under the same state identifier is limited and must not be overstated as robust tri-slice admission separation (NAD freeze).

\subsection{NAD Boundary Analysis}
NAD tracks engineered boundary controls and liminal campaigns to test whether score\_mode-only admission divergence emerges at stressed operating points. Despite higher-stress designs (NAD-LIMINAL-02 and related packs), robust divergence was \emph{not validated} at the explored points. This negative result is scientifically meaningful: PRB-governed guards and snapshot-based admission can produce differentiated scores without producing stable, reproducible admission label separation across eMBB/URLLC/mMTC under frozen thresholds.

\subsection{Core Runtime Attribution}
CORE-EXEC probes ($n{=}60$) show multidomain observability with pressure\_max $\approx 0.264$ under core contention regimes. Controlled campaigns did not demonstrate core-driven admission movement; core metrics are \emph{contributive} to telemetry and audit, not causal drivers of admission recomputation. UPF-first transport paths remain insufficient to establish core dominance (CORE-08).

\subsection{NCM Operational Contention}
NCM-ORCH-01 (36 probes, 144 burst submits) measures portal submit-path HTTP latency under orchestration load. Mean latency $\approx 4.49$\,s and max $\approx 5.52$\,s compare to sub-second baseline (${\sim}9\times$ ratio). Pressure\_max remained $\approx 0.159$ with guard-skipped triplets; orchestration contention is operationally observable but \emph{not} pressure-causal under frozen mathematics (NCM-06).

\subsection{Lifecycle Persistence}
LIFE-EXEC maps persistence classes: SEM SQLite (intents, nests, slices), Kubernetes CRDs (10,014 TriSLAReservation; 9,899 NSI objects in freeze snapshots), BC immutable registration, DE ephemeral evidence files, and portal submit metadata without a durable list API (\texttt{GET /api/v1/sla} returns 404). NASP reconciliation (60\,s interval) is continuous; SLA-Agent Kafka consumption is not wired from \texttt{main} under the frozen digest.

\subsection{Detached Orchestration}
ORCH tracks establish admission-before-orchestration ordering and detached execution (Portal$\rightarrow$NASP \texttt{/api/v1/nsi/instantiate}$\rightarrow$CRD). Code and runtime audits found no NSI$\rightarrow$DE callback and no orchestration-driven updates to score, pressure, or feasibility after instantiate.

\subsection{Runtime Taxonomy and Causal Boundaries}
Aggregating SR, NAD, CORE, NCM, LIFE, and ORCH yields a consistent taxonomy: admission is preventive and observable; transport/core are contributive; orchestration and lifecycle reconciliation are persistent and reconciliatory but detached; multidomain balanced causality and closed-loop orchestration are \textbf{non-causal} under digest \texttt{ca600174…}. Fig.~9 (cross-track convergence) and Fig.~10 (claims matrix) summarize this model for readers.



## VII. Limitations and Future Work

TriSLA's evaluation exposes structural boundaries that should accompany any deployment claim.

\textbf{Admission and slicing.} Robust tri-slice admission divergence was not demonstrated at NAD liminal operating points. Score differentiation does not imply admission-label separation under frozen PRB guards.

\textbf{Orchestration and feedback.} Orchestration is detached: no NSI$\rightarrow$decision-engine callback, no orchestration-driven pressure or feasibility updates, and no admission recomputation triggered by reconcile events.

\textbf{Core and multidomain causality.} Core metrics are observable but not admission-causal under contention campaigns. Multidomain balanced causality is not claimed; RAN-dominant behavior is explicit.

\textbf{Lifecycle and governance loops.} Continuous autonomous reevaluation is absent (SLA-Agent Kafka loop unwired). Persistence is fragmented—no unified SLA registry API. Portal list retrieval is unavailable.

These limits are properties of the frozen digest and audited wiring, not tuning oversights. Future implementation may add callbacks, durable registries, and continuous consumers; such extensions require a new digest and fresh evidence packs.



## VIII. Conclusion

This paper presented TriSLA, a digest-frozen preventive SLA-aware runtime for O-RAN-oriented network slicing. We showed that SLA feasibility can be assessed at request time using semantic interpretation, PRB-governed score\_mode admission, telemetry snapshots, detached orchestration, cluster reconciliation, and immutable submit-time governance—while explicitly characterizing subsystems that remain decoupled from admission recomputation.

\textbf{Proven under frozen evidence.} Preventive admission (SR); PRB-governed pressure at decision time; semantic persistence (SEM); detached orchestration with CRD persistence and periodic reconciliation (ORCH/LIFE); immutable BC registration; operational HTTP latency under orchestration contention (NCM); and formal negative characterization across NAD, CORE, and lifecycle paths.

\textbf{Not proven.} Robust admission divergence; orchestration-driven admission or pressure; core-driven admission; continuous autonomous reevaluation; multidomain balanced causality; and closed-loop orchestration.

The research question is \textbf{substantially answered} with explicit causal limits—an outcome appropriate for rigorous systems papers that treat reproducibility and negative characterization as first-class contributions. Future work will explore orchestration feedback APIs, continuous SLA-Agent loops, unified lifecycle registries, and session-scale campaigns under new digests without weakening frozen PRB invariants.



## References

See `references_4.bib` (IEEEtran style).