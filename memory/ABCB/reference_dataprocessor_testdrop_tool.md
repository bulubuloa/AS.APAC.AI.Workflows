---
name: reference-dataprocessor-testdrop-tool
description: "The QA self-service tool for triggering UAT data processor runs without SFTP credentials or a mail client — Lambda benefit-dataprocessor-testdrop-uat behind a Function URL. Use when QA asks support to drop a test file, or when extending it to more clients."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 66f1050d-864d-410b-9652-ec7a47df5c98
  modified: 2026-08-13T05:34:34.498Z
---

Built 2026-08-13 so QA stops asking support to place test files on the SFTP.

- Lambda **`benefit-dataprocessor-testdrop-uat`** (python3.12), Function URL auth NONE, gated by a shared
  passcode in the `TOOL_PASSCODE` env var. Same VPC/subnets/SG + role `lambda_exec_Identity` as
  `common-benefit-lambda-pullfile-sftp-*`, which is what lets it reach both S3 and the UAT RDS.
- One function serves everything: **GET** returns the HTML page, **POST** does the drop — no second host, no CORS.
- Source lives in the session scratchpad (`dptool/lambda_function.py`), not in the repo. Move it into a
  repo if it is going to be maintained.

Runs under its own least-privilege role **`benefit-dp-testdrop-uat-role`** (not the shared
`lambda_exec_Identity`): `s3:PutObject` on the four UAT prefixes only, `batch:SubmitJob` on the UAT queue
and the two job defs that need it, plus VPC/logs. A leaked passcode cannot reach prod.

What it does per client — mirrors what each processor actually reads:

- **MSC** — file to `data-processor-sftp/uat/clients/msc/` **plus** the `customer_import_file_template`
  PENDING_INSERT row (the job takes its work from that row, not the S3 event); its rule starts the job.
- **SOR** — file to `aspire-internal-app/staging/clients/sompo/` plus the queue row, then the tool
  **submits the Batch job** (SOR is schedule-driven, no S3 rule).
- **AOI** — file to `sftp-aspirelifestylesasia-com/aioi/aioi_development/…`, no queue row, tool submits
  the job (its EventBridge rule is DISABLED). Wired but never exercised.
- **HOT/HOG/MBZ/PBC/TPI/FWD** — a **fresh** MIME message into the SES prefix. Worth using even though QA
  can email, because a hand-sent *reply* hides attachments in the quoted part and the processor then sees
  none ([[reference-reply-chain-email-no-attachment]]).

**Gotcha found while building it:** `sompo-import-data-client-uat-job-definition` and
`aoi-import-data-client-uat-job-definition` set `ENV=UAT`, which the code never reads —
`GetEnvironment.ENV` is `LOCAL_PREPROD ?? CONNECTION_TARGET ?? "LOCAL"`. Without a `CONNECTION_TARGET=UAT`
container override those jobs resolve LOCAL and try to reach `127.0.0.1:3375`, a developer tunnel, from
Fargate. The tool passes the override on submit; the job definitions themselves are still unfixed.

UAT-only by construction — no production target exists in the code. ~4 MB per drop (Function URL limit).
KUC, KPI, SMC, CHU, AEON, TMI, MIT, TYT, TRI, TTR, KXA, MSU, MAZ, MSH have no UAT job definition at all,
so they are deliberately absent rather than silently doing nothing.

Open items the user has not decided: shared passcode on a public URL (could move to Cognito/WAF), and the
UAT connection string sitting in a Lambda env var rather than Secrets Manager (matches existing practice;
switching needs `secretsmanager:GetSecretValue`).
