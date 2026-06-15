# TriSLA — Canonical SLA Model (GSMA / 3GPP–aligned target)

**Versão:** 0.1 (modelagem — FASE 1 do runbook GSMA)  
**SSOT do processo:** `docs/TRISLA_GSMA_ALIGNMENT_MASTER_RUNBOOK.md`  
**Estado:** proposta de alvo; **não** substitui payloads operacionais até validação E2E.

---

## 1. Problema que este modelo resolve

Hoje, o Portal constrói `nest_template` com `sla_requirements` = **todo** o `form_values` (dict plano), misturando:

- requisitos de rede / QoS admissíveis (latência, throughput, disponibilidade);
- metadados de negócio / operação (prioridade, dispositivos, continuidade, edge);
- texto semântico (`service_description`);
- identificadores de template (`template_id`).

O contrato interno do SEM-CSMF (`SLARequirements`) espera sobretudo **latency, throughput, reliability, jitter, coverage**, enquanto o pipeline semântico enriquece com campos livres. Isso reduz a legibilidade **GSMA-like** (serviço de rede claramente separado de “contexto de negócio”) e dificulta mapeamento explícito a **SST/SD** quando desejado.

---

## 2. Princípios

1. **Compatibilidade:** o envelope legado `template_id` + `form_values` permanece aceite; a canonicalização é **adição**, não substituição abrupta.
2. **Separação:** `service_requirements` (requisitos admitidos / métricas) ≠ `semantic_context` (augmentation, linguagem natural, políticas de negócio).
3. **Diferencial TriSLA:** `semantic_context` preserva intenção em NL e atributos não-3GPP que sustentam score semântico e XAI.
4. **3GPP naming (opcional):** `slice_service_type`, `sst`, `sd` como campos **opcionais** derivados ou fornecidos quando houver mapeamento estável — sem obrigar SST/SD no MVP se isso quebrar templates existentes.

---

## 3. Schema alvo (JSON lógico)

```json
{
  "slice_service_type": "eMBB",
  "sst": null,
  "sd": null,

  "service_requirements": {
    "latency_ms": null,
    "throughput_dl_mbps": null,
    "throughput_ul_mbps": null,
    "reliability_ratio": null,
    "availability_ratio": null,
    "jitter_ms": null,
    "coverage": null,
    "mobility": null,
    "device_count": null
  },

  "semantic_context": {
    "template_id": "semantic-embb-template",
    "service_description": "",
    "priority": null,
    "security_profile": null,
    "service_continuity": null,
    "edge_processing": null,
    "business_criticality": null,
    "raw_form_values_ref": "backward_compatible_blob"
  }
}
```

### 3.1 `slice_service_type`

- Valores alinhados ao `SliceType` atual: `URLLC`, `eMBB`, `mMTC` (ou normalização única acordada com SEM-CSMF).

### 3.2 `sst` / `sd`

- **Opcional.** Mapeamento 3GPP quando política de slice e registo NST/NSST existirem no laboratório.
- Se ausentes: `null` e o pipeline continua só com `slice_service_type`.

### 3.3 `service_requirements`

- Subconjunto **canónico** derivado de `form_values` + interpretação SEM-CSMF.
- Unidades explícitas no nome do campo (`*_ms`, `*_mbps`, `*_ratio`) para evitar ambiguidade (“99.95” percentagem vs ratio).

### 3.4 `semantic_context`

- Tudo o que **não** for requisito de rede estrito mas influencia decisão, XAI ou governança editorial.
- `raw_form_values_ref`: ponteiro lógico ao dict original (ou embed completo em fase de transição) para auditoria e equivalência.

---

## 4. Mapeamento desde o estado atual

| Origem atual | Destino canónico |
|--------------|------------------|
| `form_values.service_description` | `semantic_context.service_description` |
| `form_values.priority` | `semantic_context.priority` (e/ou `business_criticality` derivado) |
| `form_values.expected_devices` | `service_requirements.device_count` |
| `form_values.mobility_profile` | `service_requirements.mobility` |
| `form_values.availability_target` | `service_requirements.availability_ratio` (após regra de parse explícita) |
| `form_values.latency` / ms strings | `service_requirements.latency_ms` |
| `template_id` | `semantic_context.template_id` + sinalização de perfil |
| Inferência SEM-CSMF `service_type` | `slice_service_type` |

---

## 5. Consumo por módulo (alvo)

| Módulo | Consome principalmente |
|--------|-------------------------|
| **ML-NSMF** | `service_requirements` + telemetria; features já numéricas |
| **Decision Engine** | `service_requirements` para SLOs canónicos; `semantic_context` para fatores semânticos / metadados |
| **BC-NSMF** | SLOs flatten para contrato; derivados de `service_requirements` + slice |
| **NASP Adapter** | `slice_service_type` / perfil + identificadores intent/nsi |
| **SLA-Agent** | `intent_id`, contratos telemetria, estado ciclo; opcionalmente deltas sobre `service_requirements` |
| **Portal** | Aceita legado; opcionalmente aceita envelope canónico quando estiver ativado por feature flag |

---

## 6. O que este documento **não** faz

- Não altera thresholds, pesos ou código.
- Não exige certificação GSMA ou conformidade 3GPP total — define **alvo editorial e de dados** para maturidade crescente.
- Próximos passos: ver runbook — FASE 2 (canonicalization layer) e gates.
