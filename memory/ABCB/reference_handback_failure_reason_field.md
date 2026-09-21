---
name: reference-handback-failure-reason-field
description: "Handback summary.json failure-reason field must be \"processedFailureReason\" (not \"errorMessage\") to show in the report's Failure Reason column"
metadata: 
  node_type: memory
  type: reference
  originSessionId: dad5ab62-3a2f-44e2-8993-ad23e763106c
---

The Data Processor handback report (ABF `DataProcessorReport.razor` / `HandbackReport.razor`) has a **"Failure Reason"** column bound to `HandbackRunListItem.ErrorMessage`. The runs API (`GET api/clients/handback/runs`, a backend NOT in the ABCB/ABF local repos) reads the S3 `summary.json` and maps its **`processedFailureReason`** field into `ErrorMessage`.

Gotcha (ABE-4839): MSU's branch (`hoang/data-processor-KXA-onboarding`) had `HandbackRunSummary.ErrorMessage` serialized as `[JsonProperty("errorMessage")]`. TMI's live `summary.json` (the current contract) uses **`processedFailureReason`**. So MSU's failed runs showed the row + status but a **blank Failure Reason** — the API ignored `errorMessage`. Fix = change the JsonProperty in `DataProcesser/Services/Handback/HandbackModels.cs` to `processedFailureReason` (shared base → fixes MSU/TTR/TRI/KXA). Verified: failed `summary.json` then emits `"processedFailureReason": "Failed to decrypt the file."`, matching TMI.

Gotcha #2 (ABE-4838 MAZ, 2026-06-04): a SECOND dev later added a brand-new `ProcessedFailureReason` property ALSO tagged `[JsonProperty("processedFailureReason")]` — alongside the renamed `ErrorMessage` from Gotcha #1. Newtonsoft then throws `A member with the name 'processedFailureReason' already exists` on EVERY `JsonConvert.SerializeObject(runSummary)`, so `UploadRunSummaryAsync` fails and **no `summary.json` is written for any client** — silently, because the only catch in `PublishHandbackAsync` just logs `[Handback] Upload failed`. Symptom: category reports (success/invalid/error) + original upload fine but the run never appears in the ABF report. Latent: only bites a client once its image is rebuilt from current source (older images keep working). Fix = removed the dead `ErrorMessage` property (never set/read; base class assigns `ProcessedFailureReason`), leaving one property → one JsonProperty. Also null-guarded `originalFileBytes` in `PublishHandbackAsync` (file-level "no files" rejection passed null → `MemoryStream(null)` threw `Value cannot be null (buffer)`). Lesson: only ONE member may carry `[JsonProperty("processedFailureReason")]`.

Also note the ABF-side consuming model `HandbackRunSummary.cs` is a slim/stale copy (only FileName/ProcessedStatus/ProcessedAt + flat counts, no ErrorMessage) — the real deserialize+map lives in the runs API backend (separate repo). TMI is the reference for the handback contract. See [[reference_masterdata_ids_env_specific]].
