import pytest

pytest.importorskip("guardrails")

from guardrails_physics_consistency.validator import PhysicsConsistency  # noqa: E402


def test_speed_of_light_fail():
    v = PhysicsConsistency()
    r = v.validate("The signal travels at 4.0e9 m/s through the cable.", {})
    assert r.outcome == "fail"
    assert "speed_of_light" in r.error_message


def test_absolute_zero_fail():
    v = PhysicsConsistency()
    r = v.validate("The chamber was cooled to -300 C.", {})
    assert r.outcome == "fail"


def test_probability_fail():
    v = PhysicsConsistency()
    r = v.validate("Confidence: 1.8 probability of success.", {})
    assert r.outcome == "fail"


def test_clean_text_passes():
    v = PhysicsConsistency()
    r = v.validate("The drone climbs at 8 m/s for 30 s.", {})
    assert r.outcome == "pass"


def test_unknown_units_ignored():
    v = PhysicsConsistency()
    r = v.validate("The flux reached 42 flibbity per squank.", {})
    assert r.outcome == "pass"


def test_kinematics_crosscheck():
    v = PhysicsConsistency(kinematics_json='{"v0":0,"a":9.8,"t":3.0,"v":50}')
    r = v.validate("As stated, v = 50 m/s.", {})
    assert r.outcome == "fail"


def test_determinism():
    v = PhysicsConsistency()
    a = v.validate("mass = -3 kg and speed 2.5e8 m/s", {})
    b = v.validate("mass = -3 kg and speed 2.5e8 m/s", {})
    assert str(a) == str(b)
