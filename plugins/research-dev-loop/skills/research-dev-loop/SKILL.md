---
name: research-dev-loop
description: >
  Autonomous research → plan → implement → test loop with minimal user supervision.
  Each stage is mirrored into an Obsidian wiki vault for persistent, cross-cycle progress
  tracking. Per cycle: (1) research the goal and file findings to the wiki, (2) draft a
  plan and have Codex critique it, (3) implement with a post-implement Codex review and
  commit, (4) write and run tests, (5) if tests fail OR doubts remain, loop back to step 1.
  Terminates only when tests pass AND no open doubts remain. Commits after each successful
  stage. Triggers on: "/research-dev-loop", "research-dev-loop", "research dev loop",
  "autonomous dev loop", "auto research loop", "research implement test loop".
allowed-tools: Read Write Edit Glob Grep Bash WebSearch WebFetch TaskCreate TaskUpdate TaskList Skill
---

# research-dev-loop: Autonomous Research → Plan → Implement → Test Loop

You drive a self-contained, sequential workflow that takes a user goal and iterates:
**research → plan (Codex-reviewed) → implement (Codex-reviewed) → test → decide.**

Every stage's artifact is mirrored into an Obsidian wiki vault so you have persistent
memory across cycles and the user has a readable audit trail.

The user opted into autonomy. Don't ask for confirmation between stages. Pause only for:
- Truly ambiguous goal (one tight clarifier, then proceed).
- Scope drift discovered mid-cycle (surface before continuing).
- Same blocker hit 3+ cycles in a row.
- Genuinely destructive actions outside the loop's scope (force-push, schema drops, etc.).

---

## Before Starting

**First, always**: Read `references/program.md`. It defines every numeric cap, Codex
usage policy, research/commit style, wiki path convention, and domain-specific override
this skill uses. Treat its values as session config for the entire run. **If anything in
this body conflicts with `program.md`, the program file wins** — the body is the
algorithm, `program.md` is the policy.

1. **Restate the goal in one sentence.** If `args` is empty or vague, ask one tight
   clarifier first. Otherwise just restate so the user can correct course early.

2. **Detect the wiki vault.** Probe (in order):
   - A `wiki/` directory in the working dir.
   - A `.obsidian/` marker anywhere up to the repo root.
   - Existing `index.md` + `log.md` at the working dir root.

   If none: ask whether to (a) bootstrap via `Skill(skill="claude-obsidian:wiki")`,
   (b) create a local `./wiki/` for this run only, or (c) skip wiki logging entirely.

3. **Environment checks** (run in parallel):
   - Git repo? If not, ask whether to `git init`.
   - Working tree clean? If dirty, stop and ask.
   - Codex available? If `codex:rescue` skill isn't loaded, tell the user to run
     `/codex:setup` first.

4. **Track stages with TaskCreate.** Add tasks for: research, plan + codex review,
   implement + codex review, tests, decide. Mark each as `in_progress` when entering
   and `completed` when leaving. Don't batch updates.

5. **Open a cycle entry in the wiki.** Append to `<vault>/log.md`:

   ```markdown
   ## Cycle <N>: <goal restatement> — <YYYY-MM-DD>
   - **Status**: in_progress
   - **Started**: <ISO timestamp>
   ```

   Use `obsidian-cli` (preferred — `Skill(skill="obsidian:obsidian-cli", args="...")`)
   or a direct Edit if the CLI isn't available. Cycle number `<N>` = count of existing
   `## Cycle` headings + 1.

6. **Open an in-memory doubts log.** Bullet list of "things I'm uncertain about" — seeded
   from the user's goal, grown by research, drained by implementation and tests.

---

## Step 1 — Research

**Goal**: a filed research note that informs the plan.

1. **Codebase research**: Glob/Grep for related files, existing patterns, prior art.
   Cite by `path:line`.

2. **Web research**: WebSearch + WebFetch for unknowns, library docs, algorithmic
   background, security/perf considerations. Honor `Loop Constraints → Max web
   operations per cycle` and `Max codebase searches per cycle` from `program.md`.
   If the topic keeps expanding, narrow scope and continue rather than busting the cap.

3. **Prior-cycle recall** (when N > 1): use `Skill(skill="claude-obsidian:wiki-query",
   args="...")` to check whether a past cycle already explored adjacent ground. Don't
   redo work that's already in the vault.

4. **Write the research note** to `<vault>/research/<slug>-cycle-<N>.md` with
   frontmatter:

   ```yaml
   ---
   type: research
   cycle: <N>
   goal: <goal restatement>
   created: <YYYY-MM-DD>
   status: complete
   ---
   ```

   Body: findings (bulleted with citations), open questions, recommended direction.
   Use wikilinks (`[[plans/...-cycle-<N>]]`, `[[log]]`) for cross-references.

5. **Update the doubts log** with anything research couldn't resolve.

6. **Cross-link** from the `log.md` cycle entry: add a `- Research: [[research/...-cycle-<N>]]`
   bullet under the cycle heading.

---

## Step 2 — Plan + Codex review

**Goal**: a Codex-reviewed implementation plan, filed and committed.

1. **Draft the plan** to `<vault>/plans/<slug>-cycle-<N>.md` with frontmatter:

   ```yaml
   ---
   type: plan
   cycle: <N>
   status: draft
   created: <YYYY-MM-DD>
   ---
   ```

   Body must cover:
   - Files to add/modify (with brief rationale).
   - Step-by-step implementation order.
   - Test strategy (what to verify, how).
   - Risks / known unknowns.
   - Link back to `[[research/...-cycle-<N>]]`.

2. **Hand the plan to Codex for critique**:

   ```
   Skill(
     skill="codex:rescue",
     args="Critique the implementation plan at <ABSOLUTE PATH to plans/...md> for goal: <goal>. Identify missing edge cases, structural issues, and verifier-friendly improvements. Read-only — do not modify files."
   )
   ```

3. **Reconcile Codex's feedback**:
   - Apply concrete improvements directly to the plan page.
   - For any Codex point you reject, add an Obsidian callout in the plan:
     ```markdown
     > [!info] Rejected Codex suggestion
     > <one-line summary of suggestion>. Reason: <why>.
     ```

4. **Flip plan status** from `draft` → `reviewed` in frontmatter.

5. **Commit plan + research artifacts**:
   ```bash
   git add <vault>/research/ <vault>/plans/ <vault>/log.md
   git commit -m "plan(cycle <N>): <one-line summary>"
   ```
   Follow the project's commit-message conventions — check CLAUDE.md / project memory
   for attribution rules (some projects require or forbid Co-Authored-By trailers).

---

## Step 3 — Implement + Codex review

**Goal**: working code committed in coherent chunks.

1. **Implement top-to-bottom** against the plan. Small, reviewable diffs. Run quick
   smoke checks (typecheck, lint) as you go. If smoke checks fail, fix before moving on.

2. **Hand the uncommitted diff to Codex** for an implementation review:

   ```
   Skill(
     skill="codex:rescue",
     args="Review the uncommitted implementation against the plan at <ABSOLUTE PATH>. Goal: <goal>. Look for bugs, missed plan branches, security/perf issues, and unhandled edge cases. Read-only — do not modify files."
   )
   ```

3. **Reconcile** the review the same way as step 2 — apply concrete fixes, document
   rejections as callouts in the plan page (not the code).

4. **Commit the implementation**:
   ```bash
   git add <impl files>
   git commit -m "impl(cycle <N>): <one-line summary>"
   ```

5. **Log to wiki**: append under the cycle entry in `log.md`:
   ```markdown
   - Implementation: `<commit SHA short>` — <one-line summary>
   ```

---

## Step 4 — Tests

**Goal**: green suite that exercises the new behavior.

1. **Write tests** covering:
   - Golden path.
   - Plan-identified edge cases.
   - Anything testable from the doubts log.

2. **Run the suite**. If it's slow (>30s expected), use `Bash` with `run_in_background`
   and Monitor for completion — don't poll.

3. **On failure**: triage (test bug vs impl bug), fix, re-run. Cap per `Loop
   Constraints → Per-stage test retry cap` in `program.md`. If still failing,
   don't loop here — let step 5 route you back to research with the failure as
   the next cycle's focus. Honor the `Test Policy → Flake handling` rule:
   a test that passes on rerun is still a fail and blocks exit.

4. **On green**: commit tests:
   ```bash
   git add <test files>
   git commit -m "test(cycle <N>): <one-line summary>"
   ```

5. **Log results** to the cycle entry:
   ```markdown
   - Tests: `<commit SHA short>` — N passed, M failed (M=0 on success). Notes: <flakes, coverage gaps>.
   ```

---

## Step 5 — Decide: loop or exit

Evaluate the loop's exit conditions:

| Condition | Action |
|---|---|
| Tests pass AND doubts log empty | **Exit.** See "On exit" below. |
| Tests pass BUT doubts remain | **Loop to step 1**, scoped to the top unresolved doubts. |
| Tests still failing after step 4 cap | **Loop to step 1**, with the failure as the next cycle's research focus. |
| Same root blocker recurs across `Same-blocker abort threshold` cycles (per `program.md`) | **Stop and ask the user.** Link the cycle entries that hit it. |
| Cycle count reaches `Max cycles per session` (per `program.md`) | **Stop and ask the user** how to proceed. Don't silently exit. |

### On loop
- Increment `<N>`.
- Append a new `## Cycle <N+1>` heading to `log.md` linking to the previous cycle:
  `- Continues from: [[#Cycle <N>: ...]]`.
- Carry forward only the unresolved doubts; clear resolved ones.
- Return to **Step 1** in the same conversation. Do not call `ScheduleWakeup` — this
  loop is synchronous by design.

### On exit
- Update the final cycle entry: `**Status**: complete`, `**Ended**: <ISO timestamp>`.
- Append an `### Outcome` block summarizing: what shipped, commit SHAs, residual notes.
- Post a short (3–5 line) summary to the user with the commit list and a link to the
  cycle entry. Then stop.

---

## Operational rules

- **Wiki ops**: prefer `Skill(skill="obsidian:obsidian-cli", ...)` for create/update of
  vault pages. Direct Read/Write/Edit is acceptable when the CLI would be heavier than
  the change. Path conventions live in `program.md → Wiki Paths & Conventions`.
- **Codex calls** follow `program.md → Codex Usage`: fixed call points at step 2 and
  step 3, read-only, one adaptive escalation allowed per cycle.
- **Commits** follow `program.md → Commit Style`: message format `<stage>(cycle <N>):`,
  one commit per stage, and **never** add AI/Claude attribution (no `Co-Authored-By`
  trailers, no "Generated with Claude Code" footers, no AI-source comments).
- **Never `--no-verify` or `--amend`** of already-pushed commits. New commits only.
- **Don't pause between stages for permission.** The whole point is autonomy.
- **Pause when scope drifts.** If research reveals the goal is materially different from
  what was asked, surface that and confirm direction before continuing.
- **TaskCreate is the source of truth for cycle stage progress.** Keep it in sync.
- **Don't fabricate citations.** Every research bullet links to a file path, URL, or
  prior wiki page. Confidence labels and source preferences come from
  `program.md → Research Style`.
- **Respect prior cycles.** Use `claude-obsidian:wiki-query` to recall before re-deriving.

---

## Constraints

Every numeric cap and policy choice is defined in `references/program.md`:

- **Loop Constraints**: max cycles per session, max web/codebase ops per cycle,
  same-blocker abort threshold, per-stage test retry cap, per-cycle Codex calls.
- **Codex Usage**: fixed call points, effort flag rules, prompt style, reconciliation
  outcomes, escalation rule.
- **Research Style**: source preference order, citation rules, confidence labels,
  voice, length.
- **Wiki Paths & Conventions**: artifact locations, frontmatter requirements, slug
  derivation, wiki-op tool preference.
- **Commit Style**: message format, scope, attribution, hook policy.
- **Test Policy**: coverage minimums, framework detection, flake handling, slow-suite
  handling.
- **Domain Notes**: per-project overrides.
- **Exclusions**: never-do list.

If a constraint conflicts with cycle completion, **respect the constraint** and record
what was left out in the cycle entry's `### Open Doubts` block. The user can re-invoke
or relax `program.md` if needed.
