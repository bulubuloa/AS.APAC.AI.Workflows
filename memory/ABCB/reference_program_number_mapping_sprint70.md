---
name: reference_program_number_mapping_sprint70
description: "ProgramNumber facts behind the epic ABE-5148 switch (sprint 70, 2026-09-21) — env-specific numbers for KUC/MSH, the shared SMC/BBK number, CHU never assigned programs before, KTC/SMC volumes"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 84a3942d-ec01-44a6-8e79-5d611c64bb41
  modified: 2026-09-21T02:31:37.746Z
---

Epic ABE-5148 moved every data processor onto `Programs.ProgramNumber` (shared helper `DataProcesser/Common/ProgramTierLookup.cs`; legacy report clients collect rows via `Services/Handback/HandbackRowCollector.cs`). Verified against UAT (tunnel 3375) and PROD (tunnel 3382) on 2026-09-21:

- **Same number in both envs**: TRI 2851121116, TTR 2851120730, MSU 2851120762, TMI 2851120063/56/60, AEO 285SSC796715, MAZ 2851118387 (UAT also has a junk 'testtest' program on the MAZ client), CHU 285MTT1066373, KTC 1310196011-15, SMC 1110199501-06, KPI 027782A34501.
- **Env-specific** (constants switch on `CONNECTION_TARGET == "PROD"`, overridable by `KUC_PROGRAM_NUMBER` / `MSH_PROGRAM_NUMBER`): KUC PROD `285KUC102687877` vs UAT `888999`; MSH PROD `285SSC1066385` (program 135 with the same number is soft-deleted) vs UAT `285SSC10663851`.
- **ProgramNumber is NOT unique**: `1110199503` is on SMC program 118 *and* BBK program 133 in both envs → the helper prefers the program whose ClientId belongs to the calling client.
- Tier names are stored as plain text or `{"en": "..."}` JSON with random whitespace — never compare the raw string, use `ProgramTierLookup.TierNameMatches`.
- CHU's import never assigned a program (PROD: 114 of 117 imported customers had none); ABE-5153 now attaches program 122 / tier "Chubb Kids Privilege Customers" on insert and to touched customers lacking it.
- KUC UAT program 595 has `Programs.ClientCode = NULL`, so the old `ClientCode == "KUC"` lookup attached nothing in UAT.
- KTC RPT2 files are ~167 MB (millions of rows) and SMC ~5 MB PGP; their report detail lists are capped at 200k rows per category (counts stay exact). KTC last received a file 2025-09; SMC EventBridge rules are DISABLED.

**How to apply:** when onboarding/changing a client's program mapping, run the SQL check in both envs first; never hardcode numeric program ids (see [[reference_masterdata_ids_env_specific]]). Related: [[reference_dataprocesser_new_client_pattern]], [[reference_handback_failure_reason_field]].
