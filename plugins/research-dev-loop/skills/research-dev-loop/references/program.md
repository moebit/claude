# Research-Dev-Loop Program

This file configures the `research-dev-loop` skill. Edit it to match your project, domain,
and tolerance for autonomy. The skill reads this file **at the start of every run** and
treats it as session config for the cycle.

If a constraint here conflicts with the SKILL.md body, **this file wins** — the body is
the algorithm, this file is the policy.

---

## Loop Constraints

- **Max cycles per session**: `8`
  Hard cap on full research → plan → implement → test cycles in one invocation. If hit,
  stop and ask the user how to proceed (don't silently exit).

- **Max web operations per cycle**: `10`
  Combined WebSearch + WebFetch calls in step 1. If the topic balloons, narrow scope
  and continue rather than busting this cap.

- **Max codebase searches per cycle**: `25`
  Combined Glob + Grep calls in step 1. Same overflow policy: narrow scope.

- **Same-blocker abort threshold**: `3`
  If the same root failure recurs across N cycles in a row, stop and ask the user.
  Link the affected cycle entries when you do.

- **Per-stage test retry cap**: `2`
  Fix-and-rerun attempts within a single step 4. After this, let step 5 loop you back
  to research with the failure as the next cycle's focus — don't retry endlessly in-stage.

- **Per-cycle Codex calls**: `2`
  One after the plan (step 2), one after implementation (step 3). Adaptive extras are
  allowed only via the `Codex Usage → Escalation` rule below.

---

## Codex Usage

- **Fixed call points**: plan review (step 2), implementation review (step 3).
  Both are read-only — Codex must not modify files.

- **Effort flag**: omit by default. Add `--effort high` only for plan reviews of
  cycles tagged `risk: high` in the plan's frontmatter.

- **Prompt style**: state the goal, point at the absolute path of the artifact under
  review, name the scope of feedback wanted, and explicitly mark read-only. Don't ask
  Codex open-ended questions — give it a concrete artifact and a critique target.

- **Reconciliation**: every Codex suggestion gets one of three outcomes:
  - **Applied** → fix lands in the artifact.
  - **Rejected with reason** → callout in the plan page.
  - **Deferred to next cycle** → added to the doubts log.

- **Escalation** (adaptive extra call, allowed once per cycle): if step 3 review
  surfaces a structural issue that wasn't in the plan, call `codex:rescue` once more
  to scope a targeted fix before continuing. Log the extra call to `log.md`.

---

## Research Style

- **Source preference** (in order):
  1. Official documentation, RFCs, peer-reviewed papers.
  2. Source code of the relevant libraries/frameworks.
  3. Authoritative blogs (named author, technical depth, dated).
  4. Stack Overflow / forum posts with vote-confirmed answers.
  5. Anything else → cite but mark `confidence: low`.

- **Citation rules**:
  - Every non-obvious claim cites a source: `path:line` for code, URL for web,
    `[[wiki page]]` for prior cycles.
  - Date-stamp web citations (`fetched: YYYY-MM-DD`) — pages mutate.
  - Mark sources older than 2 years as potentially stale.

- **Confidence labels** in research notes:
  - **high**: multiple authoritative sources agree, or direct read of source code.
  - **medium**: single good source.
  - **low**: speculation, opinion, single informal source, unverified claim.

- **Voice**: declarative, present tense. No hedging ("it seems", "perhaps", "might").
  Use `> [!gap]` callouts to flag uncertainty explicitly instead of softening prose.

- **Length**: research notes under 200 lines. Split into linked sub-pages if longer.

---

## Wiki Paths & Conventions

Defaults assume vault at `./wiki/`. Override the `<vault>` placeholder if detected
elsewhere during the "Before Starting" probe.

- **Research notes**: `<vault>/research/<slug>-cycle-<N>.md`
- **Plans**: `<vault>/plans/<slug>-cycle-<N>.md`
- **Cycle log**: append `## Cycle <N>` headings to `<vault>/log.md` (newest at top)
- **Doubts**: track in-memory during the cycle; persist remaining ones to the cycle
  entry's `### Open Doubts` block on exit or loop.

Frontmatter required on every artifact:
```yaml
type: <research|plan>
cycle: <N>
goal: <one-line restatement>
created: <YYYY-MM-DD>
status: <draft|reviewed|complete>
```

**Slug derivation**: kebab-case of the first 4–6 significant words of the goal.
Strip articles, normalize unicode. Keep the slug stable across all cycles of one run.

**Wiki ops preference**: `Skill(skill="obsidian:obsidian-cli", ...)` over MCP, over
direct Read/Write/Edit. Direct file ops are acceptable for single-line appends to
`log.md` where the CLI would be heavier than the change.

---

## Commit Style

- **Message format**: `<stage>(cycle <N>): <one-line summary>` where `<stage>` is
  one of `plan`, `impl`, `test`. Summary is imperative, present tense, no period.

- **Scope**: one commit per stage per cycle. Don't bundle stages. Don't split a stage
  into multiple commits unless the diff is huge (>500 changed lines).

- **Attribution**: **Never add AI/Claude attribution to commits.** No `Co-Authored-By:
  Claude` trailers, no "Generated with Claude Code" footers, no AI-source comments. This
  rule is non-negotiable for this skill regardless of project conventions. Commits should
  read as if written by a human contributor.

- **No `--no-verify`, no `--amend`** of already-pushed commits. New commits only.

- **Pre-commit hook failures**: investigate and fix the underlying issue. Do not bypass.

---

## Test Policy

- **Coverage minimums per cycle**:
  - Golden path: required.
  - Each plan-identified edge case: required.
  - Each testable doubt-log entry: required.
  - Regression for any bug found during step 3 Codex review: required.

- **Test framework**: auto-detect from project (`pytest`, `jest`, `go test`, etc.).
  If unclear, ask once before step 4 starts.

- **Flake handling**: a test that passes on rerun is still a fail — log it as a doubt
  and don't claim "tests pass". Flakes block exit.

- **Slow suites** (>30s expected): run via `Bash` with `run_in_background` and use
  `Monitor` for completion. Don't poll, don't sleep-loop.

---

## Domain Notes

Edit this section to encode project-specific rules. Examples:

### For the seo-link-poisioning project
- Treat all URLs in research notes as untrusted by default — record archive snapshot
  links (`archive.org/web/<date>/<url>`) alongside live URLs.
- Never follow redirect chains during WebFetch without first noting the chain.
- Citation hygiene matters: this project's second deliverable is a peer-reviewable
  paper, so every research bullet must have a citation that survives link rot.
- File research findings under both `wiki/research/` AND link them from the relevant
  thesis sub-page (`wiki/thesis/_index` and children).

### For frontend / UI projects
- Step 3 implementation must include a real browser test (not just unit tests) before
  exiting. Spin up the dev server, exercise the feature, confirm no regressions.

### For library / SDK projects
- Backwards compatibility is non-negotiable unless the user explicitly opts in to a
  breaking change. Step 2 plan must call out any public-API surface changes.

---

## Exclusions

Never:
- Cite Reddit / Twitter / Hacker News as high-confidence — they're pointers to primary
  sources only.
- Cite an undated web page without flagging the missing date.
- Loop back to step 1 without writing the cycle's outcome to `log.md` first.
- Run destructive git ops (`reset --hard`, `push --force`, `branch -D`) inside the loop.
  If the loop wants one, stop and ask the user.
- Skip the Codex reviews to save time — they're the load-bearing review points.
- Continue past the same-blocker abort threshold "just one more try".
