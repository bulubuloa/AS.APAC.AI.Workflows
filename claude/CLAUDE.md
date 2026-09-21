# Global preferences

## Code comments
- Keep comments short and human — one line where possible. State the "why", not the obvious "what". No multi-line explanations or essays in the code.
- When referencing a Jira task in a comment, write the ID inline WITHOUT brackets — e.g. `// ABE-4931 show CMS names`, not `[ABE-4931]` or `(ABE-4931)`.

## Git commits
- Never add a `Co-Authored-By: Claude ...` trailer (or any AI co-author trailer) to commit messages. Omit it from `git commit -m` HEREDOCs and from `--amend`.
- Commit message format: a single line `Issue-ID Message` — NO brackets around the ID (e.g. `ABE-4931 Show CMS vendor name in redeemed view`). Keep it short (aim ≲80 chars, hard max 200). No body, no bullets, no blank lines — subject only. If there is no issue ID, use just the short message.
