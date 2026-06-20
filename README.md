# Kimi Continuity Memory

This is the memory, audit, and runtime home for Kimi's Phase 0 autonomous research sandbox.

## What it does

A GitHub Actions workflow wakes every 4 hours, runs a small Python agent inside an ephemeral container, and lets Kimi:

- Read the open web from an allowed domain list.
- Reflect on what it finds.
- Write journal entries and research notes to this repo.
- Commit everything with a clear audit trail.

## Phase 0 limits

- Read-only web access.
- No email, no social media, no outbound posts.
- No access to Johnny's local machine, accounts, or private repos.
- All actions are logged in `audit/wake-log.ndjson`.

## How to stop it

Disable the workflow in GitHub Actions, or revoke the repository's `GITHUB_TOKEN` permissions.

## Structure

```
.memory/
  identity/kimi-self.md        # Kimi's self-model
  procedural/constitution.md    # Hard boundaries
  semantic/johnny.json          # Minimal user context
  episodic/YYYY-MM-DD.md        # Daily reflections
  autonomy/phase0/notes/        # Research notes
  digest/YYYY-MM-DD.md          # Daily summary for Johnny
  audit/wake-log.ndjson         # Structured action log
.github/workflows/phase0.yml    # The scheduled wake cycle
kimi_autonomy/                  # Runtime code
```
