---
name: abf-permissions-jwt-and-db-map
description: "ABF permissions live only in the JWT (no refresh path works), and which MySQL schema on the 3374 tunnel backs which environment"
metadata: 
  node_type: memory
  type: project
  originSessionId: 975c5b14-924c-42f5-9c93-63b06bd7803a
  modified: 2026-07-31T08:56:18.631Z
---

In ABF, role permissions are carried **only** inside the JWT — `CustomAuthenticationStateProvider.GetClaimsFromJwt` reads the `Permission` array; there is no permission API call. Consequences verified 2026-07-31:

- Changing a role's permission matrix does **not** affect anyone already signed in. They must log out and back in.
- SignalR token regeneration is dead in this client: no `CascadingValue` provider for `HubConnection`, no receiver for `ReceiveRegenerateTokens`, and `TryInitialize` is commented out everywhere. `UserRoles.razor:137` would NRE if reached. Do not "fix" stale permissions by uncommenting the `SendRegenerateTokens` calls.
- `POST api/identity/user/refreshtoken` returns 401 on UAT even with a token+refreshToken pair minted seconds earlier, so `AuthenticationManager.TryForceRefreshToken()` is not a usable workaround either.

MySQL tunnel on `127.0.0.1:3374` (`mysql -uadmin -p<password from secret benefit-connection-string-preprod → connectionStringBenefitUat>`), schema → environment:
- **`AspireProdBackup` is the DB behind `api-benefit-uat.aspireasia.net`** despite the name. Confirmed by matching a JWT `nameidentifier` against `users.Id`.
- `Aspire`, `AspireSITCopy`, `BenefitPreProd2`, `BenefitPreProdV3` are separate.

`roleclaims` stores two rows per granted permission — `IsCrossCountry` 0 and 1. A role holding only the `IsCrossCountry=0` row is a data inconsistency, not a duplicate.

Related: [[abe-5091-vendor-permission-matrix]]
