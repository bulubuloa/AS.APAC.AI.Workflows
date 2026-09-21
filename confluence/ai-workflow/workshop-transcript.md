# AI in the Development Workflow — presenter transcript

Workshop, 90 minutes. Spoken text per slide, plus what to do on screen. Timings are targets: Basics + rules
25 min · steps 15 min · examples 20 min · kit 10 min · hands-on 30 min (overlaps with Q&A).
Deck: https://claude.ai/artifact/SBYBmowEM8cChep4gFVN6p (download as .pptx from the page).

---

## 1 · Cover (0:00)

Good morning everyone, thanks for coming. This session is about how we work with an AI coding agent on our
projects — Benefit and RoadSide. It is not a product demo. Everything I will show you actually ran on our
own repositories this month: real tickets, real commits, real mistakes.

The plan is simple. First the basics — what the pieces are. Then how the workflow works, step by step. Then
two real examples, one big, one small. Then the kit that lets you set all of this up in fifteen minutes.
And the last thirty minutes you do it yourselves, on a ticket from your own board.

Please interrupt me with questions. That is more useful than saving them for the end.

## 2 · What you leave with today (1:30)

Four things. One: you understand the way we work — six steps, five rules, and the line between what the
agent does alone and what it never does. Two: you have seen two real examples so you know what "good"
looks like. Three: you have the kit installed on your machine. Four: you have fetched and analysed one
real ticket with the agent, and read the analysis critically.

One more thing: you do not need to take notes. Every slide is on Confluence, under "AI in the Development
Workflow", and everything technical is in the ai-workspace repo. Listen, ask, try.

## 3 · An agent without context guesses (3:00)

This is the one idea behind the whole workshop. An AI agent is a very fast, very well-read colleague who
has never seen our code, never seen our databases, and does not know that the preprod cluster is stopped
or that the same stored procedure is different in production.

If you give it a ticket and nothing else, it guesses — and it guesses confidently. That is the dangerous
part. If you give it the context a developer has — the ticket, the code across our four repos, the
databases in three environments, the CMS, the logs, the pipelines, and the things we learned the hard way
— it works like a colleague. It fetches, traces, verifies, implements and documents.

So every step in the workflow exists for one of two reasons: to give the agent a piece of context, or to
give a human a chance to check what it did with it. Keep that in mind and everything else follows.

## 4 · MCP — how the agent reaches our systems (5:00)

Let's start with the plumbing, because people ask about it first. MCP stands for Model Context Protocol.
Think of it as the plug standard between an agent and an external system.

On the left is the agent — Claude Code or Codex, running in your terminal, inside the repo. It decides
which tool to call, and it shows you every call.

In the middle are the plugs. An MCP server exposes named functions — get Jira issue, search with JQL, read
a Confluence page, add a comment. We use two servers. Atlassian is hosted; you authenticate once with your
own ISOS account, OAuth, and every call runs as you. Playwright is a local process — a real browser the
agent can navigate, click and screenshot.

Below that are ordinary command-line tools: aws, git, dotnet, mysql, sqlcmd, twg. Those are not MCP, and
that is deliberate — a CLI over an SSH tunnel is easier to audit and easier to keep read-only than a
database plug.

On the right, our systems: Jira, Confluence, Bitbucket, the SIT, UAT and PROD databases, AWS, Kontent, and
the running applications.

Two things to remember. Every call is made with your login, so nothing the agent does is anonymous. And
every tool is either on an allow list — silent — or prompted. We will come back to that.

## 5 · The five things the agent runs on (7:30)

These are the nouns for the rest of the talk. Five things, all plain files.

Instructions — the CLAUDE.md, or AGENTS.md for Codex. This is the map: which folder is which repo, which
branch deploys to which environment, our conventions, and what the agent must never do. There is one
global, one for the workspace, one per repo.

Slash commands — task-fetch, task-analyse and so on. A slash command is a repeatable procedure written in
Markdown. You type the command, the agent reads the file and follows the steps. The same text works as a
Codex prompt. Later I will open one so you can see there is no magic in it.

Memory — one fact per file. Environment ids, drifted procedures, incidents, gotchas. Loaded when a session
starts, written when a ticket ends, and committed to the kit so everyone has it.

Permissions — an allow list and a deny list. Reads are silent, writes are prompted. The reviewed baseline
is in the kit; your personal extras stay on your machine.

Tools — the MCP servers and the CLIs from the previous slide, each authenticated as you.

All five live in one repository called ai-workspace. One script installs them. A pull request improves
them. None of them contains a secret.

## 6 · How it fits together (10:00)

Here is the whole picture on one slide. Left: you, the developer. You give the ticket and the rules, you
review at the gates, and you run the few things the agent may not run.

In the middle, the agent. Above it is what it knows — the instructions, the commands, the memory. Below
it is what it can do — the MCP tools, the CLIs, and the permissions that gate them. The agent reads the
brief, locates the code, measures the data, decides, implements, verifies, and drafts the hand-off. And it
appends every step to one file: issues/ABE-something.md.

On the right, the outputs: that task file with the analysis and the evidence, commits on the right branch,
the PR text, the Jira comment for QA, the release lines, and new memory notes.

So: top row is what it knows, bottom row is what it can do, and the boxes on the sides are where you
decide. Every slide from here on is a zoom into one part of this picture.

## 7 · Five ground rules (12:00)

Before the steps, the rules. Five.

One, the agent acts as you. Every Jira comment, every commit, every MCP call carries your identity. So you
read what it writes before it leaves your machine.

Two, reads are silent, writes ask. Reading Jira, Confluence, code, and SELECT on a database — allowed
without asking. A comment, a push, an UPDATE, a deployment — prompted, every single time. This is the rule
people test first. Yes, it really asks.

Three, files over chat. The task file, the analysis, the evidence live on disk and later on Confluence.
Chat conversations get compacted and forgotten; files do not.

Four, cite, don't assert. A claim about code comes with file and line. A claim about data comes with the
query and the row count. Every number is tagged measured or assumption. If it cannot cite it, it does not
get to say it.

Five, the BA still decides. The agent surfaces options and blast radius. Business rules go back to the
ticket as a question. It does not decide whether three hundred providers get back-filled.

## 8 · The workflow at a glance (14:00)

Now the loop. Step zero, connect — that is MCP and the tools, done once per machine. Step one, fetch — the
ticket becomes a task file, the single source of truth. Step two, analyse — code, data and logs become a
root cause, a blast radius and a list of questions. Step three, implement and verify — the right base
branch, build, tests, and evidence in a real browser and the real database. Step four, review and release
— PR text, an AI review, the release page, and a human approves the production tag.

And the gates, in the amber box. You review the task file after fetch. You answer the questions after
analyse. You approve the commit, the push and the production tag. Everything between the gates the agent
runs on its own once the connections exist.

## 9 · The toolset (15:30)

Quickly, the tools by name, because you will see them in the permission prompts. Claude Code or Codex —
the agent. The Atlassian MCP — tickets, comments, Confluence reads; note that Confluence writes are
blocked on our tenant by the admin, so page creation goes through twg, the Atlassian CLI, also OAuth as
you. Playwright — the browser. The AWS CLI — CloudWatch logs, Parameter Store, Secrets Manager, Batch,
pipelines. MySQL and MSSQL clients through SSH tunnels on fixed ports. And the Kontent Delivery API, which
is public per environment.

What is not here: Sentry. RSA and Benefit log to CloudWatch, so that is where the agent looks.

## 10 · Connect — reads silent, writes ask (17:00)

Step zero in one slide. Left column, allowed without asking: getJiraIssue, JQL and CQL search, Confluence
page reads, git log and diff, dotnet build and test, aws get, describe and list, CloudWatch queries, the
database clients through the tunnels — with read-only logins on prod — and browser snapshots.

Right column, prompted every time: Jira comments and transitions, git push, PRs and tags, INSERT or UPDATE
on any shared database, Secrets Manager, SSM and IAM changes, Batch job definitions, EventBridge rules,
deployments.

Setup is one script from the kit — bootstrap.sh — which registers the MCP servers, installs the permission
baseline and links the memory. Then /mcp inside the agent to authenticate with your account. We do that
together in the hands-on part.

## 11 · Fetch — the task file is the deliverable (18:30)

Step one. You type /task-fetch and a ticket key. The agent pulls the ticket, the comments, the links, the
parent and the sub-tasks into issues/ABE-something.md — and stops. No code reading, no fixes. That is on
purpose: the value of this step is a clean brief.

Why a file and not a chat? It survives a context reset. You review the brief before any code exists, which
is the cheapest moment to fix a misunderstanding. Every later step appends to it. And a colleague can pick
it up.

On the right is the skeleton. Context verbatim, a one-sentence goal, three to seven requirements with
anything inferred tagged, checkbox acceptance criteria, out of scope, open questions, comments quoted
verbatim — verbatim, because a summary drops the one word that mattered. And then the sections the later
steps fill in.

Two minutes reading the Goal line at this point saves an hour later. I will show you a real one in the
hands-on part.

## 12 · Analyse — verify before you believe (20:30)

Step two, and this is the step that separates a useful agent from a dangerous one.

Locate: every touchpoint across the repos, with file and line — controllers, SQL, stored procedures,
front-end, sync jobs. The broad sweep goes to a sub-agent so the main session stays clean; the judgement
stays in the main session.

Measure: read-only queries on UAT and PROD, the CMS API, CloudWatch. Every number tagged measured or
assumption, every query written into the file so a reviewer can re-run it.

Decide: root cause or design, blast radius with red, orange, green, the questions only a BA can answer,
and a plan small enough to execute without re-thinking.

And the warning box. Always diff the live stored procedure across SIT, UAT and PROD before editing one.
The scripts in the repo and the three environments drift. This is not theory: both examples today found
drift, and in one of them the production procedure differs from UAT in two places.

## 13 · Implement and verify — seen working, not assumed (22:30)

Step three. Implement, left. Branch from the branch that feeds the first test environment — for the
client backend API, ABVB and ABF that is develop, which goes to SIT. Never from main. I know this because I
got it wrong this week and a colleague caught it; it is in the second example. Match the codebase, not the
textbook. Additive schema only. Build, tests, one-line commits in our format — ticket id, imperative
summary, no AI trailers. Stage only what you changed; no data files or screenshots in a product repo.

Verify, right. "It builds" is not evidence. Playwright on SIT or UAT along the acceptance criteria, with
screenshots. The analysis queries re-run — before and after counts side by side. CloudWatch for the minute
of the test. It all goes into an evidence table in the task file, and what could not be verified says why.

There are three modes for this step: process, which asks one to three questions up front; cowork, which
hands over for manual testing and asks before each commit; and auto, no questions, every decision recorded.
The agent never merges, never deploys.

## 14 · Review and release — gates, evidence, rollback (24:30)

Step four is a table of gates. On each row, the agent drafts, a human decides. The PR: the agent writes
title, summary, decisions and a test plan with evidence links; you open it. Code review: the agent does a
first pass in a fresh session — bugs, missed touchpoints, convention drift, migration safety — and the
human reviewer reads the diff plus those findings. UAT sign-off: a QA checklist from the acceptance
criteria; QA signs off. The release page: release note, script order, deploy order, post-deploy checks,
rollback; the tech lead reviews. Production: the agent prepares the tag and the checklist; a developer
tags, an approver clicks approve. Post-deploy: the agent runs the checks and records results; you confirm.

The agent never clicks Approve, never pushes a prod tag, never runs a prod script. It prepares the command;
a human runs it.

## 15 · What the agent never does on its own (26:00)

This slide answers the question everyone has: what if it does something stupid to production?

It cannot write to PROD — code, data or config. Prod queries are SELECT only, aggregate first, and no
customer rows ever appear in a conversation. It does not UPDATE or INSERT on SIT or UAT outside the
application or a reviewed script. No Secrets Manager, SSM or IAM writes. No push, PR, Jira transition or
production tag without your word — and pushing needs your Bitbucket credential anyway, which it does not
have. And it does not copy customer data between environments; the safety classifier refuses that, and the
agent writes you the script instead.

When something is refused, the agent writes the exact script, explains it, and carries on with everything
that does not depend on it. In the big example you are about to see, that cost about four minutes of human
time in a two-and-a-half-hour session.

## 16 · Six commands — the loop in the terminal (27:30)

Here is the loop as commands. task-fetch: Jira to task file; never reads code. task-analyse: touchpoints,
measured facts, root cause, blast radius, questions, plan; never writes anything but the task file.
task-implement: branch from the right base, stored-procedure drift check, code, build, tests, commits;
never pushes, never writes to shared databases or secrets. task-verify: evidence per acceptance criterion;
never applies a script to make a check pass. task-deliver: rebase check, PR text, QA comment draft — posted
only when you say yes — release lines, memory notes; never pushes, merges, transitions or deploys.

And task-run: all five in sequence, pausing after fetch and after analysis. Add --cowork to also pause
before every commit and before posting. Add --auto for no pauses at all — and never use auto on a ticket
that touches production data or payment logic.

These are Markdown files. Let me open one. [Open claude/commands/task-analyse.md on screen for 20
seconds.] Readable instructions, not magic. Anyone can improve them with a PR. The same six exist for
Codex as /prompts:task-something.

## 17 · Example 1: twelve data-processor tickets in one session (29:30)

Now the first example, and it is a big one. Sprint 70: eleven, then twelve, data-processor tickets — each
client gets program mapping by ProgramNumber, and seven of them get the handback report retrofitted onto
legacy code written by different people over several years, each with its own file format.

The numbers. Two prompts to start the two phases, plus eight short follow-ups. Twenty-four commits, one per
client per change. Twelve of twelve clients verified end to end on UAT, with a database check of the
program and tier each customer received. Four real defects found by real runs that unit tests had not
caught. And about four minutes of human time on the actions the agent may not take.

The first prompt, at 8:43 in the morning, was one sentence: check my issues in sprint 70, all data
processor updates, some clients just program number, some also the handback report, implement all, one
commit per client. That is it. No repo names, no file names.

Phase one — analysis and implementation of all eleven — took forty-eight minutes with no human input at
all. The developer was doing something else. Phase two — deploy to UAT, real tests, QA hand-off — took a
hundred and one minutes and five questions from the developer, and each of those questions changed the
outcome.

## 18 · What analysis found in Sprint 70 (32:30)

These are the things a "just implement it" approach would have missed. Every row came from verifying, not
assuming.

KUC and MSH have different ProgramNumbers in UAT and PROD. Found by querying the programs table in both
databases. Consequence: the constants switch on the environment; a single hard-coded value would have
silently attached nothing in one of them.

ProgramNumber is not unique. SMC's number is also on a BBK program, in both environments. Found only when
the agent simulated every new lookup together against real data, after the code was written. That became
the twelfth commit — the shared lookup now prefers the calling client's program. A unit test would never
have caught this.

CHU's import never assigned a program at all — 114 of 117 production customers have none. The ticket said
"map by ProgramNumber"; there was nothing to map. The agent implemented the assignment and then flagged it
as a behaviour change for the BA to confirm, rather than burying it.

And KTC: the files are about 167 megabytes, and a real UAT run exposed a pre-existing bug where an invalid
month aborted the whole file. Now the row is rejected with a reason and the report lists are capped.

## 19 · Example 2: one small ticket, two repos, twenty minutes (35:30)

The other end of the scale. ABE-5461: add a Job ID column and a Job ID filter to the Payment Report. One
prompt: "go with the ticket ABE-5461". Fetch one minute, analysis twelve minutes, implementation seven
minutes, two committed branches, both builds green.

Even a two-file change earned ten minutes of analysis, because two things were wrong in the environment,
not in the ticket. First, the live stored procedure behind the report is different in UAT and in PROD —
different joins and a different status filter. The obvious script, take the repo file and add a column,
would have silently changed which rows production returns. Second, the Excel header list is shared with a
legacy export; renumbering it to insert the column would have broken that export.

And the mistake: the first front-end branch was cut from main. The developer asked one question — "should
this be a PR to develop, for SIT, first?" — and that corrected it. That one question was worth more than
the twenty minutes. Process knowledge like that now sits in the instructions so the next agent does not
need the question.

On the right, the filter proven read-only on UAT data: blank returns everything, exact and lower-case and
partial each return the one row, nonsense returns zero, and the three rows that should be blank are blank.
No deployment needed to prove that.

## 20 · The kit: ai-workspace (38:30)

So how do you get all of this on your machine? One repository. Instructions — the global preferences, the
workspace map, one file per repo. Commands and permissions — the six commands, the reviewed allow and deny
list, the MCP registration. Memory — about fifty notes: environment ids, drifted procedures, pipeline
quirks, incidents. On your machine the agent's memory folder becomes a link into this repo, so a new note
is a commit. Access recipes — which tunnel port is which database, which secret holds which connection
string, CMS environments, mail rules. Names only, never a value.

Four lines: clone the kit next to the repos, run bootstrap, authenticate three things, run doctor. Doctor
prints one line per check. [If possible, run ./doctor.sh live here.]

And the task files travel with it. Work in progress is something anyone can pick up, not something in one
person's chat history.

## 21 · How knowledge stays shared (41:00)

The one rule: when a session learns something non-obvious, it becomes a memory note and it gets committed.
You review the diff like any other diff. Wrong facts get corrected or deleted — never left to mislead the
next session.

A note looks like this. A name, a one-line description used to find it, a type, and then the fact, why it
matters, and how to apply it. This one says: two tickets edited the same stored procedure and one release
script overwrote the other; so diff SHOW CREATE across environments before any procedure script. That note
is exactly why the analysis step has its warning box.

This is what made Sprint 70 fast: notes from previous tickets — the new-client pattern, a field-mapping
convention an earlier session had got backwards, environment-specific ids. Take the notes away and the
agent repeats the mistakes.

And a pre-commit guard refuses anything that looks like a token, a key or a password. Building the kit
found one real password in an old note. It is a pointer to a secret name now.

## 22 · Claude Code or Codex — same knowledge (43:00)

Some of you use Codex. Fine. The knowledge in the kit is plain Markdown, so it is agent-agnostic. The
global preferences go to AGENTS.md instead of CLAUDE.md. Each repo gets an AGENTS.md that contains the
workspace map and the repo instructions, because Codex reads from the git root and not from parent
folders. Codex has no automatic memory, so its file tells it to read the memory index at the start and
write notes at the end — the note files are identical. The six commands become prompts. The MCP servers
go into config.toml plus one login command. Permissions are coarser — a sandbox and an approval policy —
so Codex will prompt per command it cannot run in its sandbox.

Bootstrap installs both when it finds a Codex folder. Pick the agent you like. Do not let this become a
Claude-versus-Codex debate; the point is that the knowledge is shared.

## 23 · Hands-on — run the first two steps on a real ticket (45:00)

Now you. Thirty minutes, five steps.

One, setup check: run doctor. Every line OK? If not, the Setup guide on Confluence has the fix for each
line, and I will walk around.

Two, pick a ticket from your board. Something small, In Progress or To Do, with a clear description.

Three, fetch it: /task-fetch and the key. Open the task file. Is the Goal right? If not, fix it. That is
your job at this gate.

Four, analyse: /task-analyse and the file. Then read the facts table. Is every number measured? Does every
code claim have a file and line? Are the questions for the BA the right questions?

Five, pair up with a neighbour. What did it find that you did not know? What is wrong? What would you send
the BA?

And please: do not implement today. The value of this session is learning to read an analysis critically.
That is the skill this whole workflow depends on.

## 24 · Things that bit us (75:00, during or after hands-on)

While you finish, the six things you will hit in the first week, all with fixes on the Setup guide.

The MCP says write_confluence denied — expected; Confluence writes go through twg, Jira comments through
the MCP work. Diagram macros render empty — Mermaid and draw.io only render what was made in their editor;
the kit attaches images instead. Long commands wrap in the prompt and split into two — keep one-liners
short or let the agent write a script. Authentication failed for Bitbucket from the agent — expected; you
push, with an exclamation mark in front of the command. Preprod jobs die on MySQL connect — the preprod
cluster is stopped; develop and test on SIT and UAT. And ids differ per environment — clients, programs,
tiers, master data — resolve by code, never hard-code a number.

## 25 · Where everything is (80:00)

Everything from today. The series on Confluence — overview, parts zero to five, both examples. The
step-by-step Setup guide, including Codex and Windows. One page per data-processor client. The kit on
GitHub — private, ask me for access. The task files in progress inside the kit. And me, or a pull request
on the kit, for anything else.

One ask before you go: install the kit before the next sprint planning, so the first tickets of the sprint
can be fetched and analysed by the agent, and we can compare notes at the retro.

Questions?
