from src.registers import (
    decode_registers,
    decode_registers_from_offset,
    encode_state,
    register_count,
    writable_fields,
)


def test_encode_state_applies_correct_scaling():
    state = {
        "ph_value": 7.42,
        "flow_rate": 95.3,
        "pump_speed": 60,
        "ph_setpoint": 7.0,
        "pump_state": True,
    }
    registers = encode_state("dosing", state)
    assert registers == [742, 953, 60, 700, 1]


def test_decode_registers_reverses_encoding():
    registers = [742, 953, 60, 700, 1]
    state = decode_registers("dosing", registers)
    assert state["ph_value"] == 7.42
    assert state["pump_state"] is True


def test_register_count_matches_register_map():
    assert register_count("dosing") == 5
    assert register_count("raw_water") == 2
    assert register_count("distribution") == 4


def test_writable_fields_matches_register_map():
    assert writable_fields("dosing") == {"pump_speed", "ph_setpoint", "pump_state"}
    assert writable_fields("filtration") == set()
    assert writable_fields("distribution") == set()


def test_decode_registers_from_offset_maps_correct_field():
    changes = decode_registers_from_offset("dosing", address=2, values=[75])
    assert changes == {"pump_speed": 75.0}
