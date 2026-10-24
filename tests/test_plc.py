from unittest.mock import MagicMock

from plc_fleet.plc import Plc


def make_plc(stage="dosing"):
    plc = Plc(stage=stage, plant_sim_url="http://unused:8000")
    plc.client = MagicMock()
    return plc


def test_apply_state_writes_encoded_registers():
    plc = make_plc()
    state = {
        "ph_value": 7.0,
        "flow_rate": 100.0,
        "pump_speed": 50,
        "ph_setpoint": 7.0,
        "pump_state": True,
    }

    plc._apply_state(state)

    assert plc.block.getValues(0, 5) == [700, 1000, 50, 700, 1]


def test_handle_write_relays_writable_field_to_plant_sim():
    plc = make_plc()
    plc.client.actuate.return_value = {
        "ph_value": 7.0,
        "flow_rate": 100.0,
        "pump_speed": 80,
        "ph_setpoint": 7.0,
        "pump_state": True,
    }

    plc._handle_write(address=2, values=[80])

    plc.client.actuate.assert_called_once_with("dosing", {"pump_speed": 80.0})


def test_handle_write_ignores_read_only_register():
    plc = make_plc()

    plc._handle_write(address=0, values=[750])  # ph_value is read-only

    plc.client.actuate.assert_not_called()
