"""Unit tests for baseline program definitions and calorie estimation rules."""
from app.programs import PROGRAMS


def test_expected_programs_are_available():
    assert "Fat Loss (FL) – 3 day" in PROGRAMS
    assert "Fat Loss (FL) – 5 day" in PROGRAMS
    assert "Muscle Gain (MG) – PPL" in PROGRAMS
    assert "Beginner (BG)" in PROGRAMS


def test_each_program_has_required_fields():
    for program in PROGRAMS.values():
        assert program["factor"] > 0
        assert program["desc"]
        assert program["workout"]
        assert program["diet"]


def test_calorie_estimate_uses_program_factor():
    weight = 70
    assert round(weight * PROGRAMS["Fat Loss (FL) – 3 day"]["factor"]) == 1540
    assert round(weight * PROGRAMS["Muscle Gain (MG) – PPL"]["factor"]) == 2450
