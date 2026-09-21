---
name: reference-handback-run-races
description: "Two races that made Data Processor Report rows vanish — reading the newest email in the prefix instead of the triggering one, and run folders keyed only to the second. Use when report rows are missing or duplicated for a client."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 66f1050d-864d-410b-9652-ec7a47df5c98
  modified: 2026-08-11T08:04:07.461Z
---

Symptom: QA sends several test emails a minute apart and some scenarios show "no record displayed",
while other rows appear duplicated with the same file name.

**1. Wrong email.** `S3Helper.GetLastedAttachmentsFromS3(bucket, prefix)` reads the *newest* object in
the prefix, not the object that triggered the job. Concurrent jobs then all re-read the same newest
mail and the other emails are never processed. TRI/FWD/PBC always used the triggering key
(`S3_OBJECT_KEY`); HOT/HOG/MBZ did not until ABE-5149 (2026-08-11). Use
`S3Helper.GetAttachmentsForThisRun(bucket, prefix)` — it prefers `S3_BUCKET_NAME`/`S3_OBJECT_KEY`
and falls back to the newest object only when the key is unset (LOCAL).

**2. Colliding run folders.** The handback folder is `{client}/{env}/yyyyMMddHHmmss/`, so two jobs
finishing in the same second overwrote each other — one row simply disappeared. A "does summary.json
exist?" check does NOT fix it (both jobs see it free). `HandbackBatchProcessorBase` now claims the
folder with an **S3 conditional write** (`PutObjectRequest.IfNoneMatch = "*"`, PreconditionFailed →
shift one second), which needed AWSSDK.S3 3.7.205 → 3.7.416.11 (Core → 3.7.402.41). Do not suffix
the folder name — the report parses it as a timestamp.

Verify by mailing five scenarios at once and checking every one produces its own run:
[[reference-dataprocesser-uat-pipeline]].
