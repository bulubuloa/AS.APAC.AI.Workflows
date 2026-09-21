---
name: reference_dataprocesser_new_client_pattern
description: How to add a new email-triggered DataProcesser client (TRI is the template); TPI/ABE-5104 built this way
metadata: 
  node_type: memory
  type: reference
  originSessionId: a694c266-59a5-4182-810c-9e1f2b621f47
---

Adding a new email-triggered client to DataProcesser (`Clients/<CODE>/`) — model on **TRI** (config-driven + handback). Project is SDK-style, so new `.cs` files auto-compile; only **2 files need editing outside the client folder**: `Constants/JobType.cs` (add `CLIENT_<CODE>_DATA_PROCESSER` const) and `Program.cs` (add `using` + a `case` that news the processor). No central client registry; `ImportExportHeader`/`ClientSpecificConstants` need nothing.

Six files to create (clone TRI): `<C>Constants.cs` (STATUS_ACTIVE=701/INACTIVE=702, CLIENT_CODE, CLIENT_ID_EXTERNAL = Programs.ClientId, COUNTRY_ID=222, rejection-message consts + RejectionMessages[], PASSWORD_ENV_VAR, FieldMapping DTO-prop→FieldCode, DefaultFieldConfigs), `<C>Models.cs` (ExcelDTO + ExportDTO + `<C>HandbackResult : HandbackBaseResult`), `<C>CustomerAttributes.cs` (JSON keys == FieldCode), `<C>ProcessFile.cs` (`ExcelOpenHelper.OpenDataSet` password-tolerant env→Aspire@123→none; file-level validation; read cells by position; dates via cell-aware ToDateString dd/MM/yyyy — NO culture ToString, cf ABE-4983), `<C>EmailTemplate.cs`, `<C>BatchProcessor.cs : HandbackBatchProcessorBase(enableHandback:true)`.

Validation is shared: `FieldConfigValidationService.LoadFieldConfigs(clientCode)` (DB `client_customer_field_config`) merged with `DefaultFieldConfigs` via a private `MergeFieldConfigs` (DB wins IsMandatory/IsUUID; defaults fill MaxLength/Regex/DataType/EnumValues). `ValidateRow` switch TEXT/NUMBER/DATE/DATETIME/BOOLEAN/ENUM (`DataTypeValidator`). Gotchas: NUMBER = `decimal.TryParse` (accepts 12.34/1,000) — add `ValidateRegex="^[0-9]+$"` for digits-only; ENUM `ValidateEnum` is **case-sensitive** (`o.Active && o.Value==value`), EnumValues JSON `[{"Text","Value","Active"}]`.

Runtime env (EventBridge target): JOBTYPE, CLIENT_CODE, S3_BUCKET_NAME, S3_OBJECT_KEY (exact raw-email key, NOT latest-in-prefix — reads via MimeKit), CONNECTION_TARGET, RECIPIENT_EMAIL/CC_EMAIL_ADDRESSES, `<C>_EXCEL_PASSWORD`. Handback → bucket `aspire-dataprocessor-handback-report/{code}/{env}/{ts}/` (original + report/{success,invalid,error} + summary.json; summary uses `processedFailureReason`, see [[reference_handback_failure_reason_field]]). Deploy per [[reference_dataprocesser_preprod_pipeline]]. DB config for a client is authoritative (resolve masterdata/program/tier by code, cf [[reference_masterdata_ids_env_specific]]); prod DB reachable via tunnel 127.0.0.1:3382.

TPI (ABE-5104) example: client 105, UUID=PolicyNumber, 15 position-based cols, program 278 (`735290-1828622`) tier 1449, PolicyStatus enum INFORCE/ENDNO/CANCEL. Built on branch hoangq/new-client-tpi.
