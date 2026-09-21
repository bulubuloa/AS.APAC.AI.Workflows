# F23 — Environments (SIT, UAT, pre-prod, production)

**Area:** Platform · **Verdict:** Fix first · **Recommended:** one CMS environment per Roadside environment, explicit config, webhooks locked per pair

> ### Quick view for managers
> **Verdict: Fix first**
>
> **Why:** SIT and pre-prod currently read the production CMS by default, and SIT/UAT share one CMS environment. Before the CMS becomes master, each Roadside environment needs its own CMS environment and its own webhook, or test edits can reach production data.
>
> *Details, diagrams and the pros/cons of each option follow below.*

---

## 1. What it is

Which CMS environment each Roadside environment reads (and, under CMS-master, which one is allowed to write to it).

## 2. Today

```mermaid
flowchart LR
  subgraph Roadside
    SIT["Roadside SIT"]
    UAT["Roadside UAT"]
    PRE["Roadside pre-prod"]
    PROD["Roadside prod"]
  end
  subgraph Kontent
    K1[("CMS env 225b0999<br/>(SIT + UAT shared)")]
    K2[("CMS env 994226e6<br/>(PRODUCTION)")]
  end
  UAT -->|"configured Aug 2026"| K1
  SIT -.->|"no setting → code default"| K2
  PRE -.->|"no setting → code default (on purpose)"| K2
  PROD --> K2
  classDef store fill:#DCEBEC,stroke:#23656B
  classDef warn fill:#F8ECD4,stroke:#A9700F
  class K1,K2 store
  class SIT,PRE warn
```

Facts: `KontentEnvironmentId` is unset on SIT and pre-prod, so `BenefitCmsService` falls back to the hard-coded production ID. SIT and UAT share one CMS environment. The four Roadside-authored content types (`vehicle_brand`, `vehicle_model`, `engine_system`, `defect_issue`) exist only in environments where they were hand-created.

## 3. Under literal CMS-only

```mermaid
flowchart LR
  SIT["Roadside SIT"] -->|"reads PROD CMS"| K2[("CMS prod")]
  SIT -->|"vendorCmsId from SIT sync ≠ prod item ids"| EMPTY["Every provider screen empty —<br/>testers cannot reproduce anything"]
  classDef store fill:#DCEBEC,stroke:#23656B
  classDef bad fill:#F8E4E4,stroke:#A93B3B
  class K2 store
  class EMPTY bad
```

## 4. Under CMS-master with webhooks — the real danger

```mermaid
flowchart LR
  K2[("CMS prod")] -->|"webhook (if URL misconfigured)"| SIT["Roadside SIT DB"]
  K1[("CMS SIT/UAT")] -->|"webhook (if URL misconfigured)"| PROD["Roadside PROD DB"]
  classDef store fill:#DCEBEC,stroke:#23656B
  classDef bad fill:#F8E4E4,stroke:#A93B3B
  class K1,K2 store
  class PROD bad
```

A test publish rewriting production provider records is now a possible incident, not a confusing screen.

## 5. Target

```mermaid
flowchart LR
  SIT["Roadside SIT"] <-->|"read + signed webhook"| KS[("CMS SIT")]
  UAT["Roadside UAT"] <-->|"read + signed webhook"| KU[("CMS UAT")]
  PRE["Roadside pre-prod"] <-->|"read + signed webhook"| KP[("CMS pre-prod<br/>(or prod read-only, no webhook)")]
  PROD["Roadside prod"] <-->|"read + signed webhook"| KX[("CMS prod")]
  classDef store fill:#DCEBEC,stroke:#23656B
  class KS,KU,KP,KX store
```

Each Roadside site: explicit `KontentEnvironmentId`, its own webhook secret, content types replicated (the existing migration script does this).

## 6. Pros / cons

| Pros | Cons |
|---|---|
| Safe testing; reproducible bugs; no cross-environment writes | Kontent environment count and cost; content types and vendor test data must be replicated per environment |

## 7. Verdict

**Fix first** (change 13). Prerequisite for any CMS-master phase.

**Code / config:** `BenefitCmsService.cs:98, 374` (default env); `Web.config` `KontentEnvironmentId` per site; migration script `abe_kontent_env_migrate.py`.
