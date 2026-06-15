# Integrated manuscript sections for PAPER-WRITING-TRACK-03 (reviewer-safe, frozen evidence).

RELATED_WORK = r"""Network slicing has been studied extensively from architectural, orchestration, and admission-control perspectives. Surveys on 5G slicing emphasize SDN/NFV enablement, end-to-end resource isolation, and the tension between tenant-specific QoS and shared infrastructure efficiency~\cite{Afolabi2018SlicingSurvey,OrdonezLucena2017Slicing,Foukas2017Survey,Li2021E2E}. O-RAN introduces open interfaces and programmatic RAN control, yet operational platforms still require application-level admission logic that remains auditable under real deployments~\cite{Polese2022ORAN,oran_open_smart_ran,oran-survey-2023}. SLA-aware service chaining and admission frameworks address feasibility at provisioning time~\cite{Orfanos2020SFC,Sun2022SLAAdmission,Bega2021Admission,Xu2020AIAdmission}, while AI-assisted orchestration proposals often assume multidomain feedback without publishing negative paths when feedback is absent~\cite{ahmad2023ai,sharma2022aiempowered,ai-orch-2023}.

Explainable decision support and semantic intent modeling appear in parallel lines of work~\cite{Guidotti2018XAI,xai-survey,Gruber1993,Studer1998}. Blockchain-based SLA management targets immutable contracting~\cite{Zhang2020Blockchain,Ferreira2022BlockchainSLA,Javed2024Review,bao2022blockchain,choi2023slaver}, and standards bodies define reference architectures for slice management~\cite{3GPP2020NRM,3gpp28541,ETSI2021ZSM,gsma_ng116}. Platform-oriented studies such as NASP integrate 3GPP, ETSI, and O-RAN constructs in a Network-Slice-as-a-Service workflow with detailed runtime evaluation~\cite{grings2025nasp}; TriSLA differs by foregrounding preventive admission under a digest-frozen decision plane and by reporting explicit non-causal boundaries for orchestration, core, and lifecycle subsystems.

TriSLA therefore positions itself as a reproducible runtime with PRB-governed preventive admission, detached orchestration, reconciliatory cluster state, and a documented set of limits that prior slice-management papers often omit—without claiming autonomous feedback closure across admission and orchestration."""

RESULTS_EXPANDED = r"""This section reports experimental outcomes organized by metric family. Each subsection states the evaluation objective, summarizes frozen campaign evidence, interprets operational behavior, and records reviewer-safe claims together with explicit limits. Negative outcomes are treated as methodological contributions.

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
Aggregating SR, NAD, CORE, NCM, LIFE, and ORCH yields a consistent taxonomy: admission is preventive and observable; transport/core are contributive; orchestration and lifecycle reconciliation are persistent and reconciliatory but detached; multidomain balanced causality and closed-loop orchestration are \textbf{non-causal} under digest \texttt{ca600174…}. Fig.~9 (cross-track convergence) and Fig.~10 (claims matrix) summarize this model for readers."""

LIMITATIONS_FINAL = r"""TriSLA's evaluation exposes structural boundaries that should accompany any deployment claim.

\textbf{Admission and slicing.} Robust tri-slice admission divergence was not demonstrated at NAD liminal operating points. Score differentiation does not imply admission-label separation under frozen PRB guards.

\textbf{Orchestration and feedback.} Orchestration is detached: no NSI$\rightarrow$decision-engine callback, no orchestration-driven pressure or feasibility updates, and no admission recomputation triggered by reconcile events.

\textbf{Core and multidomain causality.} Core metrics are observable but not admission-causal under contention campaigns. Multidomain balanced causality is not claimed; RAN-dominant behavior is explicit.

\textbf{Lifecycle and governance loops.} Continuous autonomous reevaluation is absent (SLA-Agent Kafka loop unwired). Persistence is fragmented—no unified SLA registry API. Portal list retrieval is unavailable.

These limits are properties of the frozen digest and audited wiring, not tuning oversights. Future implementation may add callbacks, durable registries, and continuous consumers; such extensions require a new digest and fresh evidence packs."""

CONCLUSION_FINAL = r"""This paper presented TriSLA, a digest-frozen preventive SLA-aware runtime for O-RAN-oriented network slicing. We showed that SLA feasibility can be assessed at request time using semantic interpretation, PRB-governed score\_mode admission, telemetry snapshots, detached orchestration, cluster reconciliation, and immutable submit-time governance—while explicitly characterizing subsystems that remain decoupled from admission recomputation.

\textbf{Proven under frozen evidence.} Preventive admission (SR); PRB-governed pressure at decision time; semantic persistence (SEM); detached orchestration with CRD persistence and periodic reconciliation (ORCH/LIFE); immutable BC registration; operational HTTP latency under orchestration contention (NCM); and formal negative characterization across NAD, CORE, and lifecycle paths.

\textbf{Not proven.} Robust admission divergence; orchestration-driven admission or pressure; core-driven admission; continuous autonomous reevaluation; multidomain balanced causality; and closed-loop orchestration.

The research question is \textbf{substantially answered} with explicit causal limits—an outcome appropriate for rigorous systems papers that treat reproducibility and negative characterization as first-class contributions. Future work will explore orchestration feedback APIs, continuous SLA-Agent loops, unified lifecycle registries, and session-scale campaigns under new digests without weakening frozen PRB invariants."""
