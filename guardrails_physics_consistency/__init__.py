"""PHM Physics Consistency validator for Guardrails AI.

Deterministic physics plausibility checking on LLM output text.
Offline subset of the PHM physical-judgment engine: universal laws only
(speed limit, absolute zero, kinematics, conservation, probability range),
no network calls, no false positives on unknown units.
"""

__version__ = "1.0.0"
