import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from guardrails.validator_base import (
    FailResult,
    PassResult,
    Validator,
    register_validator,
)

# PHM-Lite core is vendored inside this package (zero external deps).
sys.path.insert(0, str(Path(__file__).parent))
from phm_lite import full_check  # noqa: E402


@register_validator(name="guardrails/physics_consistency", data_type="string")
class PhysicsConsistency(Validator):
    """Validates that text does not violate universal physical laws.

    **Key Properties**

    - **Deterministic**: identical input yields an identical verdict.
    - **Offline**: no network calls; no data leaves the process.
    - **No false positives on unknown units**: unrecognized unit tokens are
      ignored rather than guessed.

    Args:
        on_fail (str | Callable): failure strategy (default "exception").
        kinematics_json (str): optional JSON of SI kinematic values stated in
            the text ({"v0":0,"a":9.8,"t":3.0,"v":50}) for cross-checking.
        conservation_json (str): optional JSON {"before": {...}, "after": {...}}
            with "energy_joules" / "momentum_kg_ms" keys.
    """

    def __init__(self, **kwargs):
        self._kinematics_json = kwargs.pop("kinematics_json", None)
        self._conservation_json = kwargs.pop("conservation_json", None)
        super().__init__(**kwargs)

    def _validate(self, value: Any, meta: Optional[Dict] = None) -> dict:
        text = str(value or "")
        kinematics = None
        if self._kinematics_json:
            try:
                parsed = json.loads(self._kinematics_json)
                kinematics = {
                    k: float(v)
                    for k, v in parsed.items()
                    if k in ("v0", "v", "a", "t", "s", "h")
                }
            except (ValueError, TypeError):
                pass
        conservation = None
        if self._conservation_json:
            try:
                parsed = json.loads(self._conservation_json)
                if isinstance(parsed, dict) and "before" in parsed and "after" in parsed:
                    conservation = (parsed["before"], parsed["after"])
            except (ValueError, TypeError):
                pass

        result = full_check(text, kinematics=kinematics, conservation=conservation)
        violations = result.get("violations", [])
        if result.get("verdict") == "FAIL":
            summary = "; ".join(
                f"[{v['rule']}] {v['detail']}" for v in violations if v["severity"] == "FAIL"
            )
            return FailResult(
                error_message=f"Physics consistency check failed: {summary}",
                fix_value=text,  # value unchanged; failures here are model-side
                metadata={"violations": violations, "engine": result["engine"]},
            )
        # PASS or WARN both pass the rail; WARN details ride in metadata.
        return PassResult(
            metadata={"warnings": [v for v in violations if v["severity"] == "WARN"],
                      "engine": result["engine"],
                      "n_quantities_checked": result.get("n_quantities_checked", 0)}
        )
