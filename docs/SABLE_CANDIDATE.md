# Sable Hermes candidate — 2026-09-08

This branch is a testable, disposable compatibility layer for the four
production blockers found during the Sable migration pilot. It is **not** a
migration plan and is not installed on the live Nest.

## Base

- Upstream snapshot: `b3399c139624a0081d70397741a5b45f60fbe1f4`
- Candidate branch: `sable/hermes-candidate-20260908`

## Patch queue

Apply and remove these commits independently, in order:

| Commit | Contract | Upstream removal condition |
| --- | --- | --- |
| `d491984ad4` | `platforms.telegram.extra.preserve_backlog: true` preserves queued cold-start updates and fails safely on a startup polling conflict | Drop after PR #67656, or an equivalent fix for issue #71811, ships and passes the same conflict/backlog tests |
| `a806a1beb1` | An explicit empty parent toolset remains empty for detached Desktop/TUI tasks | Drop after issue #82010 is fixed upstream at this inheritance boundary and the regression test passes without the patch |
| `2febe1f6ac` | Desktop can execute `/skills pending`, `diff`, `approve`, `reject`, and approval-mode commands | Drop after issue #60442 has a usable Desktop review surface, whether native UI or command routing |
| `913a7ae911` | A cron result with explicit `api_calls <= 0` is recorded as failed, not successful | Drop after PR #100231, or an equivalent fix for issue #100180, ships with a behavioral `run_job` test |

The Telegram commit preserves Alexander Russell's original authorship. The
other adapted fixes credit James Skillen, AIalliAI, and Sahil Vishnalya in
their commit trailers.

## Activation

The Telegram behavior is opt-in. A future test deployment must set:

```yaml
platforms:
  telegram:
    extra:
      preserve_backlog: true
```

Do not install this candidate over the live OpenClaw Gateway. Migration and
rollback are a separate, jointly reviewed phase.

## Acceptance evidence

Focused tests on the final snapshot:

- Telegram + cron: 56 passed
- zero-tool background inheritance: 7 passed
- Desktop command routing: 33 passed
- Desktop TypeScript typecheck: passed
- Ruff, ESLint, and `git diff --check`: passed

Broad impacted-surface runs:

- Python gateway/cron surface: 1,874 passed, 19 skipped, 1 failed
- Desktop UI surface: 7,354 passed, 2 failed

The three broad-suite failures reproduce outside the patched behavior:

1. `test_model_options_preserves_canonical_custom_row_after_agent_init` —
   current upstream retains an unauthenticated Anthropic picker row.
2. Two `voice-prefs.test.ts` assertions — current upstream persists the
   local `autoSpeakReplies` value where the tests expect removal.

Neither subsystem is changed by this candidate. The blocker-specific suites,
typechecks, and linters are green.
