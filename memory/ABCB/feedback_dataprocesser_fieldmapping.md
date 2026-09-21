---
name: DataProcesser FieldMapping convention
description: How FieldMapping dictionaries are structured in DataProcesser client constants — direction and pattern
type: feedback
originSessionId: 7ab243c3-b7df-4508-8b2a-818aeb86974a
---
In `DataProcesser/Clients/<CLIENT>/<CLIENT>Constants.cs`, `FieldMapping` is a `Dictionary<string, string>` whose **key = DTO property name** (the `<CLIENT>Template` / `<CLIENT>CustomerExcelDTO` property exposed via reflection by `FieldConfigValidationService.ExtractRowValues`) and **value = DB FieldCode** (matches `client_customer_field_config.FieldCode`).

For old clients (e.g. TYT) the keys often differ from the values because the DB FieldCodes were renamed but the legacy DTO property names were kept (e.g. `ChassisNo → ChassisNumber`, `RoadsideStartDate → EffectiveDate`). For *new* clients (e.g. KXA, TTR), the DTO must use the same names as the DB FieldCodes — both sides of the dictionary are identical, and the dictionary stays in place purely to support future renames.

**Why:** `ExtractRowValues` does `type.GetProperty(mapping.Key)`; if the DTO property doesn't exist, the value comes back empty and every mandatory field fails validation. A previous attempt reversed the convention (treating keys as DB FieldCodes) and produced 100% INVALID rows on the templates.

**How to apply:** When creating a new client's constants, name the DTO properties to match the DB FieldCodes verbatim, and write `FieldMapping` with identical key/value pairs. Don't try to "bridge" legacy excel column names by inventing different keys — rename the DTO instead. Also: the parser must emit DATETIME values in `dd/MM/yyyy HH:mm:ss` (the codebase convention; `ValidateDateTime` rejects ISO `yyyy-MM-dd` form).
