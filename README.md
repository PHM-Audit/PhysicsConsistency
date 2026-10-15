# PhysicsConsistency — Guardrails AI Validator

Deterministic physics plausibility checking for LLM output. Verifies text
against **universal physical laws**: speed-of-light limit, absolute zero,
non-negativity of mass/length/energy, probability range, kinematic relation
consistency, and energy/momentum conservation.

## Usage

```python
from guardrails import Guard
from guardrails_physics_consistency import PhysicsConsistency

guard = Guard().use(PhysicsConsistency())
guard.validate("The rocket ascends at 3.0e9 m/s ...")   # -> fails: > c
```

With stated kinematic values for cross-checking:

```python
guard = Guard().use(
    PhysicsConsistency(kinematics_json='{"v0":0,"a":9.8,"t":3.0,"v":50}')
)
# fails: given v0=0, a=9.8, t=3 s, v must be ~29.4 m/s, not 50
```

## Why deterministic matters

Most output guardrails are statistical or policy-based (toxicity scores,
PII regex, model-as-judge). Physics violations are different: they are
*decidable*. A speed above c is not "probably wrong" — it is wrong under
universal law, and the verdict can be recomputed by anyone. This validator
returns exactly that class of checkable failures, with structured violation
records (`rule`, `severity`, `detail`, `location`) for downstream audit.

## Properties

- **Deterministic and reproducible** — same input, same verdict, always.
- **Offline** — no network calls; no data leaves the process.
- **No false positives on unknown units** — unrecognized tokens are ignored,
  not guessed.

## Verdict mapping

| Engine verdict | Rail result |
|---|---|
| FAIL | FailResult with rule-level error summary |
| WARN | PassResult with warnings in metadata |
| PASS | PassResult |

## Scope note

Offline universal-law subset of the PHM physical-judgment engine.
Domain-specific profiles (drone / vehicle / power-grid / molecular) ship with
the full engine via separate deployment.

MIT License.
