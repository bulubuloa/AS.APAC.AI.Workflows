---
name: abe-repo-aliases-and-cms-modules
description: "APAC Benefits repo aliases (ABVB/ABF) and key facts for CMS dynamic module work (ABE-4325 rework, DB typo, mapping table)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5ab0cbc0-d293-4c62-af57-bff4377cc33d
---

- Repo aliases: Bitbucket `apac-benefit-vendor-backend` = local `ABVB`; `apac-benefits-frontend` = local `ABF` (side by side in the workspace; folder names = the short aliases, no prefix). Integration branch is `origin/develop` in both. Bitbucket push/fetch fails locally (auth) — user pushes themselves.
- ABE-4325 (5 low-priority dynamic CMS modules) was re-implemented from scratch on 2026-06-05 because the old branch `jira/ABE-4325-dynamic-cms-module` (ABVB, commit d6e2b54) was declared incorrect/incomplete by the user (missed VendorConstants, DB mapping SQL, and all frontend work). New work lives in worktrees: `ABVB-ABE-4325` (branch `jira/ABE-4325-dynamic-cms-module-v2`) and `ABF-ABE-4325` (branch `jira/ABE-4325-dynamic-cms-module`).
- Adding a dynamic CMS module touches: ABVB — Models/KontentAICMS/ModuleX{.Generated,}.cs, Requests/KontentAICMS/ModuleXRequest.cs, CmsService.cs (typeMap + UpdateVariantAsync switch), ConstKontentAICMS.ContentTypeCodename, VendorConstants.ModuleCodename, plus a category_module_mappings SQL seed; ABF — Shared/Models/KontentAI/Modules/ModuleX.cs, VendorConstants.ModuleCodename, and 7 switch sites (AddVer2.razor ×1, EditUpdateVer2.razor ×3, Detail.razor ×3). Module types are NOT registered in CustomTypeProvider.
- Category→module mapping is DB data (`category_module_mappings` joined to `masterdatas`), not code. The masterdatas seed contains the typo 'TRAVEL AND TRASPORTATION' (missing N) — SQL must match both spellings. RESTAURANT sits under FOOD AND WINE; 'MEET & ASSIST' (not "Fast Track") under AIRPORT SERVICES — Jira ticket category columns are unreliable.
