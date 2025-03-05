"""
Tests pour les règles d'analyse avancées.
"""
import pytest
from rules import CobolRules

def test_nested_conditions():
    rule = CobolRules()
    assert rule.check_nested_conditions("IF A = B") == 1
    assert rule.check_nested_conditions("IF A = B AND IF C = D") == 2
    assert rule.check_nested_conditions("MOVE A TO B") == 0

def test_magic_numbers():
    rule = CobolRules()
    assert rule.check_magic_numbers("01 COUNTER") is False
    assert rule.check_magic_numbers("IF COUNTER > 100") is True
    assert rule.check_magic_numbers("05 FILLER") is False

def test_paragraph_length():
    rule = CobolRules()
    lines = [
        "PROCESS-DATA SECTION.",
        "    MOVE A TO B",
        "    ADD 1 TO COUNTER",
        "    IF COUNTER > 10",
        "       DISPLAY COUNTER",
        "    END-IF"
    ]
    assert rule.check_paragraph_length(lines) == 6

def test_naming_convention():
    rule = CobolRules()
    assert rule.check_naming_convention("PROCESS-DATA") is True
    assert rule.check_naming_convention("process-data") is False
    assert rule.check_naming_convention("PROCESS_DATA") is False

def test_dead_code():
    rule = CobolRules()
    lines = [
        "SECTION-A SECTION.",
        "    MOVE A TO B.",
        "SECTION-B SECTION.",
        "    MOVE C TO D.",
        "    PERFORM SECTION-A",
        "SECTION-C SECTION.",
        "    MOVE E TO F."
    ]
    dead_sections = rule.check_dead_code(lines)
    assert "SECTION-C SECTION." in dead_sections
    assert "SECTION-A SECTION." not in dead_sections

def test_data_usage():
    rule = CobolRules()
    data_lines = [
        "01 COUNTER PIC 9(4).",
        "01 UNUSED-VAR PIC X(10).",
        "01 TOTAL PIC 9(8)."
    ]
    proc_lines = [
        "MOVE 0 TO COUNTER",
        "ADD 1 TO COUNTER",
        "MOVE COUNTER TO TOTAL"
    ]
    usage = rule.check_data_usage(data_lines, proc_lines)
    assert usage["COUNTER"] == 2
    assert usage["UNUSED-VAR"] == 0
    assert usage["TOTAL"] == 1

def test_perform_thru():
    rule = CobolRules()
    assert rule.check_perform_thru("PERFORM A THRU B") is True
    assert rule.check_perform_thru("PERFORM A") is False

def test_altered_goto():
    rule = CobolRules()
    lines = [
        "PARA-A.",
        "    ALTER PARA-B TO PROCEED TO PARA-C",
        "PARA-B.",
        "    GO TO PARA-D"
    ]
    altered = rule.check_altered_goto(lines)
    assert len(altered) == 1
    assert "ALTER PARA-B TO PROCEED TO PARA-C" in altered[0]

def test_working_storage_organization():
    rule = CobolRules()
    data_lines = [
        "01 GROUP-A.",
        "   05 FIELD-A PIC X(10).",
        "   05 FIELD-B PIC 9(4).",
        "01 GROUP-B.",
        "   05 FIELD-C PIC X(5).",
        "   02 FIELD-D PIC 9(2)."  # Mauvaise organisation
    ]
    issues = rule.check_working_storage_organization(data_lines)
    assert len(issues) == 1
    assert "02" in issues[0] 