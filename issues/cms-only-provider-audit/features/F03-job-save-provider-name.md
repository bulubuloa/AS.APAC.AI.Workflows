# F03 — Saving the job with the chosen provider (and hand-typed provider names)

**Area:** Dispatching a job · **Verdict:** Can move, with conditions · **Recommended:** name from the mirror; never save a blank

> ### Quick view for managers
> **Verdict: Can move, with conditions**
>
> **Conditions to move** — all of these must be true first:
> 1. The provider name stamped on a job must never be blank — so on a CMS error the Roadside name (or the mirror) is used, never an empty value.
> 2. Hand-typed provider names on Honda / Mercedes benefit jobs must match the CMS spelling — or the option to type a name is removed now that the search box offers every vendor.
> 3. The provider record must still exist in Roadside: the job stores the Roadside ID.
>
> **What we get:** Job records carry the CMS name from the moment of save; no extra CMS call per save if the mirror is used.
>
> *Details, diagrams and the pros/cons of each option follow below.*

---

## 1. What it is

When a job is saved with a provider — picked in the search box, or implied by the vehicle the agent dispatched to — Roadside writes the provider's **name** onto the job (`JobInfo.provName`) next to the provider **ID** (`JobInfo.accountId`). That stamped name is what the monitor board, the customer link and every report show for that job, forever.

A second path: on Honda / Mercedes benefit jobs an agent may **type** a provider name without picking one. Roadside then resolves the typed text to a provider ID by exact name match.

## 2. Who uses it and how often

Every job save ≈ 150 per day, plus re-saves. One CMS call per save today.

## 3. Today

### 3.1 Architecture

```mermaid
flowchart LR
  A["Agent saves job"] --> S["MswsController.SaveJob"]
  S -->|"(1) provider by accountId:<br/>dispName, vendorCmsId<br/>no row → accountId cleared"| RDB[("Roadside DB")]
  S -->|"(2) if vendorCmsId:<br/>vendor by id (1.0–1.6 s)"| CMS[("CMS")]
  S -->|"(3) provName = CMS name,<br/>else Roadside dispName"| RDB
  S -->|"(4) typed name on benefit job:<br/>exactly one active provider<br/>WHERE dispName = typed"| RDB
  classDef store fill:#DCEBEC,stroke:#23656B
  class RDB,CMS store
```

### 3.2 Workflow

```mermaid
sequenceDiagram
  participant Ag as Agent
  participant RS as Roadside
  participant DB as Roadside DB
  participant K as CMS
  Ag->>RS: save job (accountId or vinId, or typed provName)
  alt vehicle chosen
    RS->>DB: accountId = owner of vinId
  end
  RS->>DB: SELECT dispName, vendorCmsId WHERE accountId
  alt no row
    RS->>RS: accountId = null
  else row with vendorCmsId
    RS->>K: GET vendor by id
    K-->>RS: name (or error)
    RS->>RS: provName = CMS name, fallback Roadside dispName
  end
  alt benefit job, provName typed, no accountId
    RS->>DB: SELECT accountId WHERE active AND dispName = typed
    alt exactly one
      RS->>RS: accountId = it
    else
      RS-->>Ag: "The provider X is invalid for the privilege benefit"
    end
  end
  RS->>DB: INSERT/UPDATE JobInfo (accountId, provName, ...)
```

### 3.3 Data used

| Field | Source | Purpose |
|---|---|---|
| accountId | Roadside | durable link job → provider |
| provName | CMS name (fallback Roadside) | historical display name on the job |
| dispName exact match | Roadside | resolve hand-typed name |
| BenefitVendorId | Roadside | see F04 |

## 4. Option A — literal CMS-only

```mermaid
flowchart LR
  A["Agent"] --> S["SaveJob"]
  S -->|"existence check by accountId<br/>(still required)"| RDB[("Roadside DB")]
  S -->|"vendor by id, per save<br/>error → provName = blank"| CMS[("CMS")]
  S -->|"typed name: match in CMS list<br/>(full download)"| CMS
  S --> RDB
  classDef store fill:#DCEBEC,stroke:#23656B
  classDef bad fill:#F8E4E4,stroke:#A93B3B
  class RDB,CMS store
  class S bad
```

| Situation | Result |
|---|---|
| Normal save | +1.0–1.6 s; name = CMS name ✔ |
| CMS error / 429 | job saved with **blank provider name**; blank on monitor board, customer link, reports until re-saved ✘ |
| Vendor unpublished | same as error ✘ |
| Typed name in Roadside spelling | rejected; agent must know the CMS spelling ✘ |
| Typed name on a benefit job | needs a full list download per save (2–4 s) |

| Pros | Cons |
|---|---|
| Name always CMS-current at save time | Blank names become possible on the permanent job record |
| | Slower save; typed names harder |

## 5. Option C — mirror (recommended)

```mermaid
flowchart LR
  CMS[("CMS (master)")] -->|"webhook"| M["Mirror"]
  M --> RDB[("Roadside DB<br/>dispName = CMS name")]
  A["Agent"] --> S["SaveJob"]
  S -->|"one SELECT: dispName (already CMS name)"| RDB
  S -->|"typed name: dispName = typed OR userName = typed"| RDB
  S --> RDB
  classDef store fill:#DCEBEC,stroke:#23656B
  classDef new fill:#DDEFE3,stroke:#2E7A4F
  class RDB,CMS store
  class M new
```

| Pros | Cons |
|---|---|
| 0 CMS calls per save; save is faster than today | Name is webhook-fresh, not live (a rename published 3 s before the save may stamp the old name) |
| Never a blank name | |
| Typed names match CMS spelling *and* login | |

## 6. Comparison

| | Today | A · CMS-only | C · Mirror |
|---|---|---|---|
| CMS calls per save | 1 | 1 (+1 list if typed) | 0 |
| Blank name possible | no | **yes** | no |
| Typed-name matching | Roadside spelling | CMS spelling only | both |
| Save latency added | ~1–1.5 s | ~1–1.5 s (+2–4 s typed) | 0 |

## 7. Verdict

**Can move, with conditions.** Recommended **C**. Whatever is chosen, the stamped `provName` must never be written blank — it is the historical record reports fall back to when a vendor no longer exists.

**Decision:** whether hand-typed provider names on benefit jobs remain allowed at all now that the search box can offer every vendor.
**Code:** `BkkRsa/Api/MswsController.cs:363-382, 977-989, 1027-1046`; `MswsController_JobOthers.cs:269-288 (ResolveProviderDispNameAsync)`.
