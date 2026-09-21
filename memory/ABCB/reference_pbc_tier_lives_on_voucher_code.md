---
name: reference-pbc-tier-lives-on-voucher-code
description: "PBC \"Customer Tier\" is voucher_codes.CustomerTierId, not a customer column; UAT tier ids and how to reach the UAT DB"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 184db21a-bd5c-494f-acc2-425a2bf1ac6a
  modified: 2026-08-19T15:55:43.858Z
---

For PBC (UOB Concierge) the "Customer Tier" column in the import file maps to **`voucher_codes.CustomerTierId`** — the `customers` table has **no tier column at all**. Tier names come from `client_customer_tiers.Name`, stored as locale JSON (`{"en":"PV"}`), which is why `LoadClientTierNames` parses JSON.

UAT (`AspireProdBackup`), PBC = clientId **483**, one `voucher_code_configs` row (Id 229, ProgramId 0):

- 3968 = Platinum (30000 codes) · 4136 = PV (100) · 4137 = PV+ (100)

Table names in this schema are **PascalCase columns** and the tiers table is `programscustomertiers` (no underscores), unlike `client_customer_tiers`.

Customer status ints: 701 Active / 702 Inactive / 703 Archive. `VoucherCodeStatus` = 0 Active, 1 Inactive, 2 Expired, 3 Used — verified against the live distribution, mapping is correct.

Reaching the UAT DB from a laptop needs an SSH tunnel (the RDS endpoint is VPN-gated); the user runs one on **localhost:3375**, then connect with the `connectionStringBenefitUat` credentials from Secrets Manager `benefit-connection-string-preprod`.

Related: [[reference-pbc-uat-pipeline]], [[reference-dataprocessor-testdrop-tool]]
