---
name: abe-4612-privilege-name-bug
description: "ABE-4612 bug — RSA Job privilege dropdown missing name for roadside privileges, root cause + verified fix"
metadata: 
  node_type: memory
  type: project
  originSessionId: fc8ab534-1769-4791-8374-09271e4e7712
---

ABE-4612 failed SIT 2026-05-25: "Missing Privilege name when Product Addition Method = Manually" — RSA Job (JobDetail) privilege dropdown showed no privilege.

**Root cause (verified against SIT DB):** `WebHookSyncDataRsaBenefit/Repositories/ProgramPrivilegeService/ProgramPrivilegeService.cs` → `GetListPrivilege` filtered RSA-eligible privileges by a legacy hard-coded external-product-id list (`Common.ListServiceIds` matched against `products.ProductIdExternal`). On the new ABE-4612 product data, roadside products have `ProductIdExternal = NULL`, so nothing matched → privilege filtered out → name absent. Confirmed with test privilege **2167 "Privilege Name ABE-4612"** (tier `CustomerTiersId=4072`, `ProductAdditionMethod='Manual'`, 9 AUTO/ROADSIDE products, all `ProductIdExternal` null). See [[rsa-benefit-backend-topology]].

**DB facts learned (Aspire MySQL, SIT via tunnel 127.0.0.1:3374, user app_benefit_sit):**
- `privileges.ProductAdditionMethod` values are `'Manual'` (1163), `'ByRule'` (39), null (69) — NOT "Manually".
- `products` has BOTH `ProductType` (legacy, null on new data) and `ProductTypeId` (the taxonomy one). Roadside type masterdata `MasterCode`s = REPAIR/BATTERY/BATREPL/GASOLINE/HOME/LOCK/TOWMOTOR/TOWING/TYRE. Category `ServiceId`→MasterCode `AUTO`, subcat `ServiceChildId`→`ROADSIDE`.
- ByRule privileges DO materialize matched products into `privilegeproducts` (e.g. priv 2169 has 977 roadside rows), so the inner join on `privilegeproducts` is fine for both methods — the ONLY defect was the match criterion + wrong type column.
- Tier 4086 (priv 2166, ByRule, vendor-rule "xoi", 0 roadside products) correctly returns empty — it was the wrong test case.

**Fix (branch `jira/abe-4612-fix-privilege-dropdown` in worktree /tmp/abcb-abe4612-fix off origin/roadside-sync-data-sit, builds clean):** replaced the `ListServiceIds`/`ProductIdExternal` filter with joins to `MasterDatas` matching Category=AUTO + SubCategory=ROADSIDE + ProductType code in the 9 list, joining on **`product.ProductTypeId`** (added that property to the WebHook `Product` entity). Validated by SQL: corrected query returns priv 2167 (+2169) for tier 4072, empty for 4086. Commits fe600a9e3 (initial) + d83a1bd41 (ProductTypeId correction). Not pushed/PR'd as of 2026-05-26.
