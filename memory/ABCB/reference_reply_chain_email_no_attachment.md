---
name: reference-reply-chain-email-no-attachment
description: "Data Processor jobs see zero attachments when QA replies/forwards instead of sending a fresh email — MimeKit's Attachments skips parts nested in the quoted message. Use when a client job logs only \"Result email sent.\" and publishes no handback report."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 66f1050d-864d-410b-9652-ec7a47df5c98
  modified: 2026-08-10T10:15:23.113Z
---

`S3Helper.GetLastedAttachmentsFromS3` loads only the **latest** object under the prefix and reads
`MimeMessage.Attachments`. When the tester hits *Reply* on an existing thread, the .xlsx sits inside the
nested quoted message, so `Attachments` is empty → the processor takes the "no attachment" branch,
sends the error email, and (before ABE-5149 fix) published no report at all → QA sees a blank
Data Processor Report and reports the ticket failed.

Diagnosis: the Batch log shows only `Result email sent.` with no `Start <client> ... processing` lines.
Confirm by downloading the .eml from `benefit-raw-email-receiving/{env}/EMAIL/{Folder}/` and grepping
`Content-Disposition` — a reply chain shows attachments belonging to the *quoted* message.

Fix applied 2026-08-10: HOT/HOG/MBZ now call `PublishFailedHandbackAsync(... "No attachment found in
the email.")` on that branch, matching FWD/TRI. Tell QA to send a **new** email, not a reply.
See [[reference-dataprocesser-uat-pipeline]].
