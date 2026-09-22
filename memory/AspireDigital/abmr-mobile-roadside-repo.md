---
name: abmr-mobile-roadside-repo
description: ABMR = apac_mobile_roadside, the Android "Aspire Partner" provider app; works on main with Gradle flavours, talks to ABMB api/pmws; added to the kit 22 Sep 2026
metadata:
  type: project
---

`ABMR` (`internationalsos/apac_mobile_roadside`) is the RSA **provider mobile app** (Android, Kotlin/Compose), the client of ABMB `BkkRsaPartner` `api/pmws/*`. Cloned into the workspace and added to the kit (clone/doctor/bootstrap, per-repo `CLAUDE.md`, memory folder `memory/ABMR`) on 2026-09-22. Hoang owns it (124 of ~135 commits).

**Why:** the Vietnam 2026 engineering workshop (`ai-workshop/*.pptx`) gives Hoang the "native RSA mobile app automation decision" output; the agent needs the repo alongside ABMB to trace pmws contract changes end to end.

**How to apply:** unlike every other repo, the working branch is `main` (`development` is dead). Environment = Gradle flavour (`sit`/`uat`/`prerpod`/`prod`), not branch; buildspecs per flavour push to Firebase App Distribution. CodeBuild projects for it were **not** found in account 739075353953 (ap-southeast-1 / us-east-1) — confirm with Vimukthi. `app/sec/` keystore + Firebase creds are committed: never echo them. Details in `ABMR/CLAUDE.md`; related [[abe-5457-provider-mobile-flag]] (provider login rows), [[abmb-roadside-cicd]].
