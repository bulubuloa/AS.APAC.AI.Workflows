---
name: customer-name-two-places
description: "DataProcesser must write the customer name to BOTH the core customers columns AND the CustomerAttributes JSON, or the customer LIST screen shows blank"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 7913aa43-39bb-4b75-9338-59f15922bf01
---

In a DataProcesser client, the customer name must be saved in **two places** on the `Customer` entity:
1. Core columns: `FirstNameEN`, `NameEN`, and `Name` (= the name value). `Name` is a **generated column** in `customers` — EF tolerates setting it on the entity (TTR/MSU do) but a raw SQL UPDATE of `Name` errors with "value for generated column not allowed"; backfill only `FirstNameEN`/`NameEN`.
2. The `CustomerAttributes` JSON (`FirstNameEN` key), via the field config.

The ABF **customer LIST** screen (`Pages/Customers/Customers.razor`, the `FirstNameEN` default column) binds `context.FirstNameEN`, which the customer-search API fills from the **core `customers.FirstNameEN` column** — NOT the JSON. The customer **detail/attributes** view reads the JSON. So if a processor writes only the JSON attribute (as the first MAZ/ABE-4836 build did), the detail shows the name but the LIST shows blank.

Working peers TTR/MSU set all three core columns (`existingCustomer.FirstNameEN/NameEN/Name = item.FirstNameEN`) in both the new-customer and update paths. MAZ originally set none → QA found blank name in the list. Fix: mirror TTR/MSU. See [[feedback_dataprocesser_fieldmapping]].
