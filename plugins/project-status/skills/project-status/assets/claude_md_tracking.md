## Project status tracking

This project tracks visible progress in `project_status.html` (open it in a browser to see at-a-glance status for each part of the codebase).

**When you finish meaningful work on a tracked part of the project**, you MUST also update `project_status.html` in the same change:

1. Find the relevant stage in the `STAGES = [...]` array (inside the `<script>` tag near the bottom of the file).
2. Move the matching `pending` entry into `shipped` (or append a fresh `shipped` entry with a brief ref — commit SHA, cycle number, date, or short label).
3. If `Snapshot YYYY-MM-DD` in the header subtitle is older than today, bump it.

Surgical edits only — use the Edit tool, preserve structure, don't regenerate the file. Re-invoke `/project-status` only when adding a new top-level part or doing a major reorganization.
