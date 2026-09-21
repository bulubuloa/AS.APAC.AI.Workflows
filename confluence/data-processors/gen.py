import html, os, sys, re
from clients import CLIENTS, ENV_DB

OUT = os.path.dirname(os.path.abspath(__file__)) + "/pages"
os.makedirs(OUT, exist_ok=True)
DATE = '<time datetime="2026-09-21">21 Sep 2026</time>'

def esc(s):  # values already contain intentional inline HTML (<code>, <strong>); only escape bare '&'
    return s.replace("&", "&amp;").replace("&amp;amp;", "&amp;").replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;")

import json as _json
PNGS = _json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/pngs.json")) if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/pngs.json") else {}
PAGE_IDS = _json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/page_ids.json")) if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/page_ids.json") else {}
import uuid as _uuid, datetime as _dt
MEDIA = _json.load(open(os.path.dirname(os.path.abspath(__file__)) + "/media_ids.json")) if os.path.exists(os.path.dirname(os.path.abspath(__file__)) + "/media_ids.json") else {}
def mermaid(code, size="medium", key=None):
    # Diagram = PNG attachment (rendered from the Mermaid source with mrender.html, uploaded via REST) + the source in an expand.
    # The Mermaid Chart / draw.io / PlantUML apps only render macros created in their own editor, so API-written macros stay empty.
    m = MEDIA.get(key)
    fig = ('<figure data-type="media-single" data-layout="center" data-width="100" data-width-type="percentage">'
           f'<div data-type="media" data-media-type="file" data-id="{m["fileId"]}" data-collection="{m["collection"]}" data-alt="{m["title"]}"></div></figure>') if m else '<p><em>diagram image missing — run mrender.html + upload</em></p>'
    src = '<details><summary>Diagram source (Mermaid) — paste into any Mermaid editor to change it</summary><pre><code class="language-text">' + html.escape(code) + '</code></pre></details>'
    return fig + src

def li(items):
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>" if items else "<p>None recorded.</p>"

FLOW = {
 "email": """flowchart LR
  M[Client mailbox] -->|new mail + xlsx| SES[SES receipt rule<br/>env-EMAIL-Client]
  SES --> S3[(benefit-raw-email-receiving<br/>env/EMAIL/Folder/raw .eml)]
  S3 -->|Object Created| EB[EventBridge rule<br/>client-env-email-rule]
  EB -->|InputTransformer: JOBTYPE, CLIENT_CODE,<br/>CONNECTION_TARGET, S3_OBJECT_KEY, RECIPIENT_EMAIL| B[AWS Batch job<br/>DataProcesser container]
  B -->|MimeKit reads THE triggering .eml| V[parse → validate → upsert]
  V --> DB[(Benefit MySQL)]
  V --> R[(aspire-dataprocessor-handback-report<br/>CODE/ENV/timestamp/)]
  V --> E[SES result email]
  R --> ABF[ABF Data Processor Report]""",
 "sftp-s3": """flowchart LR
  SF[Client SFTP] --> SCH[EventBridge Scheduler]
  SCH --> L[pull-file Lambda<br/>decrypts PGP where applicable]
  L --> S3[(bucket/env/clients/client/file)]
  S3 -->|Object Created, prefix| EB[EventBridge rule]
  EB --> B[AWS Batch job]
  B -->|reads S3_OBJECT_KEY| V[parse → validate → upsert]
  V --> DB[(Benefit MySQL)]
  V --> R[(handback report bucket)]
  V --> E[SES result email]
  R --> ABF[ABF Data Processor Report]""",
 "queue-row": """flowchart LR
  SRC[Client SFTP / bridge Lambda / QA tool] --> S3[(data-processor-sftp<br/>env/clients/client/)]
  SRC --> Q[(customer_import_file_template<br/>row Status = PENDING_INSERT)]
  S3 -->|Object Created| EB[EventBridge rule]
  EB --> B[AWS Batch job]
  Q -.->|job reads the row, NOT the event<br/>latest: KPI/KUC · oldest: MSC/CSM| B
  B --> V[parse → validate → upsert]
  V -->|row → INSERT_SUCCESS| Q
  V --> DB[(Benefit MySQL)]
  V --> R[(handback report bucket)]
  V --> E[SES result email]""",
 "schedule": """flowchart LR
  P[Scheduler pull hh:15] --> L[Lambda apac-benefit-pullfile-sompo-*]
  L --> S3[(aspire-internal-app<br/>env/clients/sompo/)]
  L --> Q[(queue row)]
  S[Scheduler batch hh:30] -->|submit-job, job def by NAME| B[AWS Batch job]
  S3 --> B
  Q --> B
  B --> V[parse → validate → upsert]
  V --> DB[(Benefit MySQL)]
  V --> FP[(FileProcessed/ + report)]""",
 "email-lambda": """flowchart LR
  M[3 mailboxes<br/>hongqi / mitsubishi / thaiorix] --> SES[SES rule]
  SES --> S3a[(benefit-raw-email-receiving<br/>env/EMAIL/tmi/)]
  S3a --> EB1[EventBridge rule<br/>…-eb-emailattachment]
  EB1 --> X[extractor Lambda nodejs]
  X --> S3b[(sftp-aspirelifestylesasia-com<br/>tokiomarine/tokiomarine_env/)]
  S3b --> EB2[EventBridge rule<br/>…-eb-filelanding]
  EB2 -->|CLI args bucket and key| B[AWS Batch job]
  B --> T[TMIProcessFile picks sub-template]
  T --> V[validate → upsert → report]""",
}

def client_page(c):
    code = c["code"]
    p = []
    p.append(f'<p>Client page of the <em>APAC Aspire Benefit Data Processors</em> series. Facts verified against the code (branch <code>jira/ABE-5177-…-hanback-report</code>) and the live AWS account on {DATE}.</p>')
    p.append('<div data-type="panel-info"><p>Read the <strong>Overview</strong> page first for the shared architecture, environments, deploy procedure and testing tools. This page holds only what is specific to this client.</p></div>')
    p.append("<h2>1. Identity</h2><table data-layout=\"default\"><tbody>")
    for k, v in [("Client code", f"<code>{code}</code>"), ("Client", c["name"]), ("JOBTYPE", f"<code>{c['jobtype']}</code>"),
                 ("Processor class", f"<code>{c['cls']}</code> in <code>DataProcesser/DataProcesser/{c['folder']}/</code>"),
                 ("Files", c["files"] + f" ({c['loc']} lines)"), ("Trigger pattern", c["trigger"]),
                 ("Handback report (ABF Data Processor Report)", c["report"]), ("Jira", c["jira"]), ("Docs / samples in repo", c["docs"])]:
        p.append(f"<tr><th>{k}</th><td>{esc(v)}</td></tr>")
    p.append("</tbody></table>")

    p.append("<h2>2. Pipeline per environment</h2>")
    p.append("<p>Names are the live AWS resources (account 739075353953, ap-southeast-1). <em>revision-pinned</em> means the rule target carries the job-definition revision ARN — a new revision must be repointed; <em>by name</em> means the latest ACTIVE revision is used automatically.</p>")
    p.append('<table data-layout="full-width"><thead><tr><th>Env</th><th>Entry point</th><th>Landing (S3)</th><th>Trigger rule</th><th>Batch queue</th><th>Job definition</th><th>Image</th><th>CONNECTION_TARGET</th></tr></thead><tbody>')
    for row in c["pipeline"]:
        p.append("<tr>" + "".join(f"<td>{esc(x)}</td>" for x in row) + "</tr>")
    p.append("</tbody></table>")
    p.append("<h3>Flow</h3>" + mermaid(FLOW[c["kind"]], key=code))

    p.append("<h2>3. Input file and validation</h2><table data-layout=\"default\"><tbody>")
    for k, v in [("Format", c["fmt"]), ("Reader", c["reader"]), ("Password / decryption", c["password"]), ("UUID (duplicate key)", c["uuid"]), ("Field mapping (DTO → FieldCode)", c["mapping"])]:
        p.append(f"<tr><th>{k}</th><td>{esc(v)}</td></tr>")
    p.append("</tbody></table>")
    p.append("<p>Validation for every client comes from <code>client_customer_field_config</code> (IsMandatory / IsUUID / MaxLength / Regex / DataType / EnumValues) merged with the client's <code>DefaultFieldConfigs</code> in code (DB wins). NUMBER uses <code>decimal.TryParse</code>; ENUM matching is case-sensitive; DATETIME must be <code>dd/MM/yyyy HH:mm:ss</code>.</p>")

    p.append("<h2>4. Program and tier mapping</h2><p>" + esc(c["programs"]) + "</p>")
    p.append("<p>Check before any change, in <strong>both</strong> UAT and PROD:</p><pre><code class=\"language-sql\">SELECT p.Id, p.ClientId, p.ClientCode, p.ProgramNumber, p.NameEN, p.Status, p.Deleted, t.Id AS TierId, t.Name AS TierName\nFROM programs p JOIN programscustomertiers t ON t.ProgramId = p.Id\nWHERE p.ProgramNumber = '&lt;number&gt;' ORDER BY p.Id, t.Id;</code></pre>")

    p.append("<h2>5. Deploy</h2><p>" + esc(c["deploy"]) + "</p>")
    p.append("<p>Generic steps (Overview §6): build <code>--platform linux/amd64</code> from <code>DataProcesser/</code>, push an <strong>immutable</strong> tag to the env's ECR repo, register a new job-definition revision with the new image (copy the latest revision's containerProperties), repoint the EventBridge target if it is revision-pinned, verify with <code>aws events list-targets-by-rule</code> + <code>aws batch describe-job-definitions</code>. For a brand-new env also create the SES receipt rule (email clients) — the 4th leg everyone forgets.</p>")

    p.append("<h2>6. How to test</h2>" + li(c["test"]))
    p.append("<p>Manual submit template (adjust queue / job def / env vars from §2):</p><pre><code class=\"language-bash\">aws batch submit-job --region ap-southeast-1 \\\n  --job-name \"" + code.lower() + "-uat-manual-$(date +%s)\" \\\n  --job-queue benefit-import-uat-job-queue \\\n  --job-definition benefit-" + code.lower() + "-import-uat-job-definitions \\\n  --container-overrides '{\"environment\":[\n    {\"name\":\"JOBTYPE\",\"value\":\"" + c["jobtype"] + "\"},\n    {\"name\":\"CLIENT_CODE\",\"value\":\"" + code + "\"},{\"name\":\"CLIENT_NAME\",\"value\":\"" + code + "\"},\n    {\"name\":\"CONNECTION_TARGET\",\"value\":\"UAT\"},\n    {\"name\":\"S3_BUCKET_NAME\",\"value\":\"&lt;bucket&gt;\"},{\"name\":\"S3_OBJECT_KEY\",\"value\":\"&lt;key&gt;\"},\n    {\"name\":\"RECIPIENT_EMAIL\",\"value\":\"[\\\"you@aspirelifestyles.com\\\"]\"},{\"name\":\"CC_EMAIL_ADDRESSES\",\"value\":\"[]\"}]}'</code></pre>")
    p.append("<p>Then: <code>aws batch describe-jobs --jobs &lt;id&gt;</code> for the log stream, <code>aws logs get-log-events</code> on <code>/aws/batch/job</code>, and open ABF → Data Processor Report on <strong>benefit-uat</strong> (folder <code>" + code + "/UAT/</code> in the handback bucket). A run with no row in the report but 'Result email sent.' in the log = the no-attachment branch.</p>")

    p.append("<h2>7. Known issues and gotchas</h2>" + li(c["gotchas"]))
    p.append("<h2>8. Open items</h2>" + li(c["open"]))
    p.append("<h2>9. Where the knowledge lives</h2><ul><li>Code: <code>Omnicasa.Mobile.ABCB/DataProcesser/DataProcesser/" + c["folder"] + "/</code>, shared code under <code>Common/</code>, <code>Services/Handback/</code>, <code>Constants/</code>.</li><li>Repo docs: <code>docs/data-processor/</code> (" + esc(c["docs"]) + ").</li><li>Agent memory (ABCB project): the reference notes listed on the Overview page; anything learned while working this client should be added there so the next session — human or agent — starts from it.</li></ul>")
    return "\n".join(p)

def overview_page():
    p = []
    p.append(f'<p>Last updated {DATE} · Source of truth for the Benefit <strong>DataProcesser</strong> (client customer-file imports) — architecture, environments, every client, deployment and testing. Verified against the code and the live AWS account. One child page per client.</p>')
    p.append('<div data-type="panel-info"><p><strong>Who this is for.</strong> A developer picking up a data-processor ticket, QA planning a test, and any AI agent working in the ABCB repository. If a fact here disagrees with AWS or the code, the code/AWS wins — fix the page.</p></div>')

    p.append("<h2>1. What the DataProcesser is</h2>")
    p.append("<p>A .NET 8 console application (<code>Omnicasa.Mobile.ABCB/DataProcesser/DataProcesser</code>, entry <code>Program.cs</code>) packaged as one Docker image and run as <strong>AWS Batch (Fargate)</strong> jobs. One image serves every client; the <code>JOBTYPE</code> environment variable selects the client processor in a <code>switch</code> (<code>Constants/JobType.cs</code>). Each job takes one client file (Excel, CSV, fixed-width text, PGP/zip), validates every row against the client's field configuration, upserts customers into the Benefit MySQL database (<code>customers</code>, <code>customerprograms</code>, attributes JSON), attaches the client's program/tier, emails a result, and publishes a per-row <em>handback report</em> that ABF shows on the <em>Data Processor Report</em> screen.</p>")
    p.append(mermaid("""flowchart TB
  subgraph IN[Ingestion — one pattern per client]
    direction LR
    A[Email → SES → S3]
    Bq[SFTP → pull Lambda → S3]
    C[SFTP / QA → S3 + queue row]
    D[EventBridge Scheduler]
  end
  IN --> EB[EventBridge rule<br/>S3 Object Created, prefix match]
  EB --> BATCH[AWS Batch Fargate job on the env queue<br/>JOBTYPE · CLIENT_CODE · CONNECTION_TARGET · S3_OBJECT_KEY · RECIPIENT_EMAIL]
  BATCH --> DP[DataProcesser container<br/>Program.cs switch on JOBTYPE]
  DP --> SM[(Secrets Manager<br/>DB connection string, PGP keys)]
  DP --> STEPS[read file → parse → FieldConfigValidationService → upsert EF Core → ProgramTierLookup]
  STEPS --> DB[(Benefit MySQL<br/>customers · customerprograms · attributes JSON)]
  STEPS --> MAIL[SES result email]
  STEPS --> HB[(aspire-dataprocessor-handback-report<br/>CODE/ENV/yyyyMMddHHmmss/<br/>original · report/success,invalid,error · summary.json)]
  HB --> ABF[ABF → Data Processor Report<br/>Failure Reason = processedFailureReason]""", size="large", key="00-overview"))

    p.append("<h2>2. Environments</h2>")
    p.append('<table data-layout="default"><thead><tr><th>Env</th><th>CONNECTION_TARGET</th><th>Database</th><th>ECR repo</th><th>Shared Batch queue</th><th>State</th></tr></thead><tbody>')
    p.append(f"<tr><td><strong>PROD</strong></td><td><code>PROD</code></td><td>{ENV_DB['PROD']}</td><td><code>apac-benefit-data-processer-production</code> — immutable per-client tags (<code>fwd-abe5325-20260909</code>, <code>tri-20260706-1</code>…); never reuse the bare v1.x tags</td><td><code>benefit-import-prod-job-queue</code> (KPI, KUC, MSC, MAZ, TPI, TMI) or per-client queues</td><td>Live</td></tr>")
    p.append(f"<tr><td><strong>UAT</strong> (= the development environment since 2026-07-27)</td><td><code>UAT</code></td><td>{ENV_DB['UAT']}; ABF report visible on <strong>benefit-uat</strong> only (SIT is a different DB)</td><td><code>apac-benefit-data-processer-pre-production</code> with <code>uat-&lt;ticket&gt;-&lt;date&gt;-nn</code> tags (SOR: <code>aspire-common-job-uat:latest</code>; AOI: <code>aoi-client-uat-import-data:latest</code>)</td><td><code>benefit-import-uat-job-queue</code> → CE <code>benefit-import-data-clients-uat</code></td><td>Live; account is at the hard 50 job-queue limit</td></tr>")
    p.append(f"<tr><td>PREPROD</td><td><code>PREPROD</code></td><td>{ENV_DB['PREPROD']}</td><td><code>apac-benefit-data-processer-pre-production:v1.21 / :latest</code></td><td><code>benefit-import-preprod-job-queue</code> or per-client</td><td>Rules exist and fire, jobs fail on MySQL connect — do not test here</td></tr>")
    p.append("<tr><td>LOCAL</td><td><code>LOCAL</code> / <code>LOCAL_PREPROD</code></td><td><code>LOCAL_CONNECTION_STRING</code> env var through an SSH tunnel (UAT tunnel on a local port; prod read-only tunnel on another)</td><td>—</td><td>—</td><td>DB-free <code>LocalTests/*</code> exist for HOT, TPI, FWD, KXA, TRI, TTR, KPI, TYT (uncomment one line in Program.cs)</td></tr>")
    p.append("</tbody></table>")
    p.append("<p><code>GetEnvironment.ENV = LOCAL_PREPROD ?? CONNECTION_TARGET ?? \"LOCAL\"</code>. A job definition without <code>CONNECTION_TARGET</code> (SOR UAT, AOI UAT) resolves LOCAL and dies on MySQL connect unless the override is passed at submit time. Job role for all preprod/UAT job defs: <code>AWS-Execution-Role-SIT</code> (already writes the handback bucket). EventBridge → Batch service role: <code>Amazon_EventBridge_Invoke_Batch_Job_Queue_1609455605</code>. SES active rule set: <code>benefit-receipt-ruleset-sit</code> (holds prod, preprod and uat rules despite the name).</p>")

    p.append("<h2>3. Shared code every client depends on</h2>")
    p.append('<table data-layout="default"><thead><tr><th>Component</th><th>Path</th><th>What it does / rule</th></tr></thead><tbody>')
    for a, b, c in [
        ("HandbackBatchProcessorBase", "Services/Handback/HandbackBatchProcessorBase.cs", "Base class (enableHandback:true) — claims the run folder with an S3 conditional write (IfNoneMatch=*), uploads original + category reports + summary.json. Only ONE property may carry [JsonProperty(\"processedFailureReason\")] (HandbackModels.cs) or no summary is ever written."),
        ("HandbackRowCollector", "Services/Handback/HandbackRowCollector.cs", "Sprint-70 helper for legacy processors: collects Inserted/Updated/SameData/Invalid/DuplicateUUID rows with Row No + UUID columns; optional per-category cap (200k for KTC/SMC) with exact counts."),
        ("ProgramTierLookup", "Common/ProgramTierLookup.cs", "ByProgramNumber / AllByProgramNumber: Programs.ProgramNumber + Deleted IS NULL, prefers the program whose ClientId belongs to the calling client (ProgramNumber is NOT unique — SMC/BBK share one), TierNameMatches normalises plain-text and {\"en\":…} JSON tier names. Null → caller logs and falls back to its legacy lookup."),
        ("FieldConfigValidationService", "Services/…", "LoadFieldConfigs(clientCode) from client_customer_field_config merged with DefaultFieldConfigs (DB wins IsMandatory/IsUUID). ExtractRowValues uses FieldMapping KEY = DTO property name → a wrong key = 100% INVALID rows."),
        ("S3Helper.GetAttachmentsForThisRun", "Common/", "Reads the triggering object (S3_BUCKET_NAME/S3_OBJECT_KEY); falls back to newest-in-prefix only when unset. Never use GetLastedAttachmentsFromS3 for a new client — concurrent jobs re-read the same mail."),
        ("ExcelOpenHelper / CommonDate", "ExcelHelper/, Common/CommonDate.cs", "Password-tolerant open (env → Aspire@123 → none). Date cells MUST go through CommonDate.TryParseDateCell — cell.ToString() under InvariantCulture gives MM/dd and swaps day/month (FWD, HOT incidents)."),
        ("ConnectionString / AspireContext", "Constants/ConnectionString.cs, ModelsBenefit/", "Secret benefit-connection-string-preprod keyed by ENV (UAT / PROD / PREPROD); LOCAL uses LOCAL_CONNECTION_STRING."),
        ("DecryptPgpAsync / KTCHandleFileEncrypt", "Common/", "PGP decryption with keys from Secrets Manager (AOI, KTC, SMC, SOR, MSC)."),
        ("EmailSending / EmailTemplate", "EmailSending/, EmailTemplate/", "SES result mail; recipients from RECIPIENT_EMAIL / LIST_EMAIL_TO (JSON array) + CC_EMAIL_ADDRESSES; sender EMAIL_DOMAIN (noreply@aspireasia.net). Prod RECIPIENT_EMAIL is often the team address with teammates on CC — house pattern."),
        ("Customer name", "each processor", "Write FirstNameEN / NameEN / Name core columns AND the CustomerAttributes JSON — the ABF list reads the column, the detail reads the JSON (Name is a generated column: never UPDATE it raw)."),
    ]:
        p.append(f"<tr><td><strong>{a}</strong></td><td><code>{b}</code></td><td>{esc(c)}</td></tr>")
    p.append("</tbody></table>")

    p.append("<h2>4. Client matrix</h2>")
    p.append('<table data-layout="full-width"><thead><tr><th>Code</th><th>Client</th><th>Trigger</th><th>Input</th><th>Program mapping</th><th>Report</th><th>PROD</th><th>UAT</th><th>Page</th></tr></thead><tbody>')
    for c in CLIENTS:
        prod = next((r for r in c["pipeline"] if r[0] == "PROD"), None); uat = next((r for r in c["pipeline"] if r[0] == "UAT"), None)
        def short(r):
            if not r or r[5] == "—": return "—"
            jd = r[5].split(" (")[0]; return f"<code>{jd}</code>"
        pn = "ProgramNumber" if "ProgramNumber <code>" in c["programs"] or "ProgramNumbers" in c["programs"] else ("voucher tier" if c["code"] == "PBC" else "legacy (code/ClientId)")
        rep = "Yes" if c["report"].startswith("Yes") else "No"
        p.append(f"<tr><td><strong>{c['code']}</strong></td><td>{esc(c['name'])}</td><td>{esc(c['trigger'])}</td><td>{html.escape(re.sub(r'<[^>]+>','',c['fmt']).split('. ')[0][:80])}</td><td>{pn}</td><td>{rep}</td><td>{short(prod)}</td><td>{short(uat)}</td><td>{c['code']} page (child)</td></tr>")
    p.append("</tbody></table>")
    p.append("<p>Pipelines that exist in AWS but are <strong>not</strong> in this codebase (legacy per-client images; no page): BBL Bangkok Bank (<code>benefit-import-data-bbl-clients</code>, email prod/EMAIL/BBL), BKK (<code>bkk-prod-email-rule</code> → <code>benefit-import-data-msig-clients-preprod</code> image), CZC (<code>benefit-import-customers-czc</code>, email), SCB (<code>benefit-import-data-clients-scb</code>, scheduler DISABLED), MDL Major Development (DISABLED), TGR (DISABLED, reuses the MBZ job defs), KBANK (SES rules <code>prod</code>/<code>preprod</code> catch-all), KTC one-off migration job. Treat them as frozen until someone owns them.</p>")

    p.append("<h2>5. Ingestion patterns</h2>")
    p.append('<table data-layout="default"><thead><tr><th>Pattern</th><th>Clients</th><th>Mechanics</th><th>Watch out</th></tr></thead><tbody>')
    p.append("<tr><td>A. Email</td><td>FWD, HOG, HOT, KXA, MAZ, MBZ, MIT, MSH, MSU, PBC, TPI, TRI, TTR, TYT</td><td>SES receipt rule <code>env-EMAIL-Client</code> for <code>client-env-import@aspirelifestylesasia.com</code> → raw .eml in <code>benefit-raw-email-receiving/env/EMAIL/Folder/</code> → rule <code>client-env-email-rule</code> → Batch. The processor reads the .eml with MimeKit.</td><td>Reply-chain mails hide the attachment in the quoted part → 'no attachment'. Missing SES rule = sender gets 550 'mailbox not available' while everything else looks fine. Bucket-wide <code>benefit-extract-attachment-lambda-sit</code> also drops extracted attachments back into the prefix.</td></tr>")
    p.append("<tr><td>A′. Email + extractor Lambda</td><td>TMI</td><td>Three mailboxes → S3 → extractor Lambda → file lands in the Transfer Family bucket → rule passes <code>--bucket/--key</code> CLI args.</td><td>Only client using CLI args; mutable <code>tmi-latest</code> tags.</td></tr>")
    p.append("<tr><td>B. SFTP pull → S3 drop</td><td>AEO, CHU, KTC (+ AOI direct Transfer Family drop)</td><td>Scheduler → pull-file Lambda (<code>common-benefit-lambda-pullfile-sftp-production</code>, <code>benefit-pullfile-sftp-ktc-prod</code>) → <code>aspire-internal-app/env/clients/&lt;c&gt;/</code> → rule → Batch; S3_OBJECT_KEY is the file.</td><td>The pull Lambda has hardcoded client handlers — a new SFTP client needs a handler or a bridge (see MSC).</td></tr>")
    p.append("<tr><td>C. S3 + queue row</td><td>KPI, KUC, SMC, MSC, CSM</td><td>File in <code>data-processor-sftp/env/clients/&lt;c&gt;/</code> (or aspire-internal-app for SMC) <strong>and</strong> a <code>customer_import_file_template</code> row PENDING_INSERT; the job reads the row, not the event.</td><td>Only one PENDING_INSERT row at a time (KPI/KUC take the latest → older rows orphaned; MSC/CSM take the oldest). The S3 upload itself fires a job — insert the row after that job finishes or you double-import. Row claim is not atomic except CSM.</td></tr>")
    p.append("<tr><td>D. Scheduled</td><td>SOR</td><td>Scheduler pulls (hh:15) then submits the job (hh:30) by job-def NAME.</td><td>UAT schedules disabled; UAT job def lacks CONNECTION_TARGET.</td></tr>")
    p.append("</tbody></table>")

    p.append("<h2>6. Deploying a change</h2>")
    p.append("<ol><li><strong>Build &amp; push</strong> from <code>DataProcesser/</code>: <code>docker buildx build --platform linux/amd64 -t 739075353953.dkr.ecr.ap-southeast-1.amazonaws.com/&lt;repo&gt;:&lt;immutable-tag&gt; --push .</code> (a build without <code>--push</code>/<code>--load</code> pushes nothing). Do not run <code>MacOS_ECR_Push.sh</code> blindly — it has pointed at the production repo before.</li>")
    p.append("<li><strong>Register a job-definition revision</strong>: copy the latest revision's <code>containerProperties</code>, replace <code>.image</code>, <code>aws batch register-job-definition --type container --platform-capabilities FARGATE</code>. Keep every env var (JOBTYPE, CLIENT_CODE, CONNECTION_TARGET, RECIPIENT_EMAIL…).</li>")
    p.append("<li><strong>Repoint the rule</strong> when its target pins a revision ARN (most email rules): <code>aws events list-targets-by-rule</code> → set <code>BatchParameters.JobDefinition</code> to the new ARN → <code>aws events put-targets</code>, preserving the InputTransformer. Rules that reference by name (KPI, KUC, MSC, MSH, HOG, MIT prod, TMI, SOR, all sprint-70 UAT defs) need nothing.</li>")
    p.append("<li><strong>New environment for a client</strong> also needs: SES receipt rule (<code>aws ses create-receipt-rule --rule-set-name benefit-receipt-ruleset-sit --after &lt;neighbour&gt;</code>) with the S3 prefix matching the EventBridge pattern exactly; a job queue only if a shared one cannot be used (50-queue hard limit); the client row + <code>client_customer_field_config</code> in that env's DB (IDs are env-specific — resolve by code, never hardcode).</li>")
    p.append("<li><strong>Verify</strong>: <code>aws events list-targets-by-rule --rule … --query 'Targets[0].BatchParameters.JobDefinition'</code> and <code>aws batch describe-job-definitions --job-definition-name … --status ACTIVE --query 'jobDefinitions | sort_by(@,&amp;revision) | [-1].containerProperties.image'</code>, then one real run.</li>")
    p.append("<li><strong>Prod</strong>: never <code>:latest</code>; tag per client + ticket + date; leave <code>client-prod-email-rule</code> alone during a preprod/UAT bump; database scripts from <code>database/</code> run before the job def switch.</li></ol>")

    p.append("<h2>7. Testing</h2>")
    p.append("<ul><li><strong>QA test-drop tool</strong> — Lambda <code>benefit-dataprocessor-testdrop-uat</code> (Function URL + passcode, role <code>benefit-dp-testdrop-uat-role</code>, UAT-only by construction). GET = HTML page, POST = drop. Per client it does exactly what the real trigger does: fresh MIME mail into the SES prefix (email clients), file + PENDING_INSERT row (MSC, CSM, SOR), file + job submit with <code>CONNECTION_TARGET=UAT</code> (SOR, AOI). Source in <code>DataProcesser/infra/dataprocessor-testdrop/</code>. The sprint-70 clients (AEO, CHU, KTC, MSH, KUC, SMC, KPI, TRI, TTR, MSU, TMI) are being added as of 21 Sep 2026.</li>")
    p.append("<li><strong>Send a real email</strong> to the UAT mailbox — always a <em>new</em> mail, never a reply.</li>")
    p.append("<li><strong>Copy an existing S3 object</strong> to a new key under the watched prefix to re-fire the rule.</li>")
    p.append("<li><strong>Manual submit</strong> — <code>aws batch submit-job</code> with container overrides (template on every client page). Override RECIPIENT_EMAIL so the client is not mailed.</li>")
    p.append("<li><strong>Local, DB-free</strong> — uncomment one <code>*LocalTest</code> line in Program.cs; unit tests in <code>DataProcesser.Tests</code> (627 tests; <code>ProgramNumberMappingTests</code>, <code>HandbackRowCollectorTests</code>).</li>")
    p.append("<li><strong>Read the result</strong> — Batch job log stream under <code>/aws/batch/job</code>; ABF → Data Processor Report on benefit-uat; the handback bucket folder; UAT DB through the tunnel (read-only SELECTs, key on CustomerAttributes JSON where ReferenceID is unreliable).</li>")
    p.append("<li><strong>Race check</strong> — send five scenarios in one minute; each must get its own run folder and row.</li></ul>")

    p.append("<h2>8. Onboarding a new client (checklist)</h2>")
    p.append("<ol><li>Clone <strong>TRI</strong> (email + Excel) — six files: Constants (CLIENT_CODE, PROGRAM_NUMBER, PASSWORD_ENV_VAR, FieldMapping with identical DTO/FieldCode names, DefaultFieldConfigs), Models (+ HandbackResult), CustomerAttributes, ProcessFile (ExcelOpenHelper, TryParseDateCell), EmailTemplate, BatchProcessor : HandbackBatchProcessorBase(enableHandback:true). Add the JobType const and the Program.cs case. Resolve clientId from ClientCode at runtime.</li>")
    p.append("<li>DB per env: client row, <code>client_customer_field_config</code> rows (UUID, mandatory, MaxLength — check the real file first), program + tier with a <strong>ProgramNumber</strong>, masterdata resolved by MasterCode.</li>")
    p.append("<li>AWS per env: SES receipt rule → S3 prefix → EventBridge rule (InputTransformer with all env vars) → job definition (immutable image tag) → queue. Keep the rule DISABLED until the image with the new JOBTYPE is live.</li>")
    p.append("<li>Add the client to the test-drop tool; run the five-scenario race test; verify the ABF report on benefit-uat.</li>")
    p.append("<li>Write the client page here and the memory note.</li></ol>")

    p.append("<h2>9. Cross-cutting gotchas (read once, remember forever)</h2>")
    p.append(li([
        "IDs are environment-specific: clients.Id, programs.Id, masterdatas.Id, tier ids. Hardcode none of them; resolve by ClientCode / ProgramNumber / MasterCode.",
        "ProgramNumber is not unique across clients (SMC/BBK share 1110199503) and can differ per env (KUC, MSH).",
        "Tier names are plain text or {\"en\":\"…\"} JSON with stray whitespace — compare through ProgramTierLookup.TierNameMatches.",
        "FieldMapping key = DTO property name, value = DB FieldCode. Reversing it yields 100% INVALID rows.",
        "Date cells: TryParseDateCell, never ToString(). DATETIME strings: dd/MM/yyyy HH:mm:ss.",
        "Read the triggering S3 key, not the newest object; claim run folders with a conditional write (both fixed in the base class — do not bypass it).",
        "Queue-row clients: one PENDING_INSERT at a time; uploads fire their own job; the EF context is poisoned after a failure so the row can stay pending.",
        "customers has no unique index on any UUID — duplicates are only prevented in code (FWD advisory lock GET_LOCK('abcb_fwd_data_processor')).",
        "Preprod DB is stopped; UAT is where development runs. ABF report only on benefit-uat.",
        "Job-def rule targets pin revision ARNs — registering a revision alone deploys nothing for those clients.",
        "SES receipt rule is the 4th leg of every email pipeline; MAZ prod ran for weeks without one.",
        "Prod recipients are often the team, not the client — ask before 'fixing'.",
        "The Atlassian MCP can add Jira comments but cannot write Confluence on our tenant; pages are published with the twg CLI, diagrams as PNG attachments (see the AI workflow series).",
        "UAT job definitions for the sprint-70 clients (TRI TTR MSU TMI MAZ AEO CHU KTC MSH KUC SMC KPI) exist since 21 Sep 2026 on image uat-sprint70-20260921-06 with NO SES/EventBridge rules — the QA test-drop tool is the only trigger; KTC/SMC need the UAT public-key secrets it created.",
    ]))

    p.append("<h2>10. Client pages</h2>")
    p.append('<p><span data-type="inline-extension" data-extension-key="children" data-extension-type="com.atlassian.confluence.macro.core" data-parameters=\'{"macroParams":{"all":{"value":"true"},"depth":{"value":"1"}},"macroMetadata":{"schemaVersion":{"value":"2"},"title":"Child pages"}}\'>Child pages</span></p>')
    p.append("<h2>11. Related</h2><ul><li><a href=\"https://internationalsos.atlassian.net/wiki/spaces/AD/pages/6837665931\">AI in the Development Workflow — Overview</a> (how these pages get used by the agent)</li><li><a href=\"https://internationalsos.atlassian.net/wiki/spaces/AD/pages/6837895252\">Worked example — Sprint 70: 11 data-processor clients in one session</a></li><li>Repo docs: <code>docs/data-processor/</code> — testing-guide.md, deployment-to-production.md, deploy-KXA/MSU/TYT-*.md, KPI/TYT-ConfigDrivenValidation.md, the AD-*.pdf onboarding guides, sample files.</li></ul>")
    return "\n".join(p)

if __name__ == "__main__":
    open(f"{OUT}/00-overview.html", "w").write(overview_page())
    for c in CLIENTS:
        open(f"{OUT}/{c['code']}.html", "w").write(client_page(c))
    print("wrote", len(CLIENTS) + 1, "pages to", OUT)
