---
name: reference-dataprocesser-preprod-pipeline
description: AWS preprod deployment pipeline for DataProcesser — Batch job definitions per client + EventBridge rules pinned to a specific revision ARN. Use when bumping the ECR image version.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 734799ba-0e8a-45c5-b40d-f67aced60206
  modified: 2026-07-27T02:26:38.028Z
---

## DataProcesser preprod deployment topology

Region: `ap-southeast-1`. AWS account: `739075353953`.

- **ECR repo**: `apac-benefit-data-processer-pre-production`. Tags are **per-client** where clients diverge — FWD pins `fwd-1.9`, `fwd-1.10`, … not a shared `v1.x`. Check the client's current job def image before choosing the next tag.
- **DO NOT run `MacOS_ECR_Push.sh` blindly** — as of 2026-07 it points at the **production** repo (`apac-benefit-data-processer-production:tmi-latest`), not preprod. Read it first; it gets rewritten per-developer. Safer: `docker buildx build --platform linux/amd64 -t <full-ecr-tag> --push .` from `DataProcesser/` (plain `buildx build -t name` without `--push`/`--load` leaves the image in cache only and pushes nothing).
- **Per-client Batch job definitions**: `benefit-{client}-import-preprod-job-definitions` (lowercase client code, e.g. `kxa`, `tri`, `ttr`, `kuc`, `mbz`, `mitsubishi`, `toyota`, `kpi`, `honda`, `msh`, plus `sompo-import-data-client-pre-prod-job-definition`, `benefit-ktc-import-preprod`). Each new version → register a new revision with the bumped image.
- **Per-client EventBridge rules**: `{client}-preprod-email-rule` (kxa/tri/ttr observed). Targets reference job def by **revision-pinned ARN** (`...:8`), NOT by name — so registering a new revision is not enough; the rule's target must be repointed too. Target also carries `InputTransformer` env vars (JOBTYPE, CLIENT_NAME, RECIPIENT_EMAIL, etc.) that must be preserved on update.

## Bump procedure (per client)

1. Push image to ECR (one push covers all clients):
   - Edit `MacOS_ECR_Push.sh`, bump the tag on lines 5 and 7.
   - Run `bash MacOS_ECR_Push.sh`.
2. For each affected client, register new job def revision + repoint EventBridge rule. The following loop does both, preserving everything except the image (job def) and the JobDefinition ARN (target). Replace `NEW_IMAGE` and the client list:

   ```bash
   set -e
   REGION=ap-southeast-1
   NEW_IMAGE="739075353953.dkr.ecr.ap-southeast-1.amazonaws.com/apac-benefit-data-processer-pre-production:v1.19"
   for client in kxa tri ttr; do
     JD_NAME="benefit-${client}-import-preprod-job-definitions"
     RULE="${client}-preprod-email-rule"
     CP=$(aws batch describe-job-definitions --region $REGION --status ACTIVE \
           --job-definition-name "$JD_NAME" \
           --query 'jobDefinitions | sort_by(@, &revision) | [-1].containerProperties' \
           --output json | jq --arg img "$NEW_IMAGE" '.image = $img')
     NEW_ARN=$(aws batch register-job-definition --region $REGION \
               --job-definition-name "$JD_NAME" --type container \
               --platform-capabilities FARGATE \
               --container-properties "$CP" \
               --query 'jobDefinitionArn' --output text)
     TARGET=$(aws events list-targets-by-rule --region $REGION --rule "$RULE" --output json \
              | jq --arg arn "$NEW_ARN" '.Targets[0].BatchParameters.JobDefinition = $arn | .Targets')
     aws events put-targets --region $REGION --rule "$RULE" --targets "$TARGET"
   done
   ```

## Verification

```bash
for client in kxa tri ttr; do
  aws events list-targets-by-rule --region ap-southeast-1 --rule "${client}-preprod-email-rule" \
    --query 'Targets[0].BatchParameters.JobDefinition' --output text
  aws batch describe-job-definitions --region ap-southeast-1 --status ACTIVE \
    --job-definition-name "benefit-${client}-import-preprod-job-definitions" \
    --query 'jobDefinitions | sort_by(@, &revision) | [-1] | {Rev:revision, Image:containerProperties.image}' --output text
done
```

## Notes

- Older job def history shows the version cadence: v1.8, v1.10, v1.11, v1.13, v1.14, v1.15, v1.16 — gaps are normal (the user skips numbers).
- `ECR_Push.sh` (non-MacOS) pushes the `:latest` tag instead of a version; preprod batch job defs pin to version tags, so that script is not used for the preprod flow described here.
- The shared EventBridge service role: `arn:aws:iam::739075353953:role/service-role/Amazon_EventBridge_Invoke_Batch_Job_Queue_1609455605`.
- Production rules (`{client}-prod-email-rule`) also exist — same pattern but DO NOT touch them as part of a preprod bump.
- All preprod job defs share job role `AWS-Execution-Role-SIT`, which already writes the handback bucket — onboarding a new client to handback needs no IAM change.

## The 4th leg: SES inbound receipt rule (easy to miss)

ECR + job def + EventBridge rule only cover the *processing* half. Mail only lands in
`s3://benefit-raw-email-receiving/{env}/EMAIL/{CLIENT}/` if an **SES receipt rule** accepts the
recipient. Miss it and senders get a bounce — "550 / mailbox not available" — while the
EventBridge rule sits ENABLED and never fires, and the Batch queue shows zero jobs ever.

- Active ruleset is `benefit-receipt-ruleset-sit` (despite the name it holds **prod, preprod and uat** rules).
- Naming: `prod-EMAIL-{CLIENT}` / `preprod-EMAIL-{CLIENT}`; recipient `{client}-{env}-import@aspirelifestylesasia.com`;
  S3 action prefix must match the EventBridge pattern prefix exactly (`prod/EMAIL/{CLIENT}/`).
- Create with `aws ses create-receipt-rule --rule-set-name benefit-receipt-ruleset-sit --after <neighbour> --rule '{...}'`.
  It takes effect immediately since that ruleset is active.
- Triage order for "mailbox not available": SES rule exists+enabled → S3 prefix has objects → Batch job history.
- 2026-09-02: MAZ prod had image v1.21, job def `benefit-maz-import-prod-job-definitions:2` and
  `maz-prod-email-rule` all deployed, but no `prod-EMAIL-MAZ` SES rule — nothing ever reached prod. Added it.

## RECIPIENT_EMAIL in prod is the team, not the client

Prod EventBridge targets for TRI, MSU and MAZ all set `RECIPIENT_EMAIL` to
`hoang.quach@aspirelifestyles.com` with teammates on CC. This is the house pattern, **not** a
misconfiguration — don't "fix" it to a client address without asking.
