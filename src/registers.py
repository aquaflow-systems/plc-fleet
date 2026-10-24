from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterDef:
    address: int
    name: str
    scale: float
    writable: bool
    is_bool: bool = False


STAGE_REGISTERS: dict[str, list[RegisterDef]] = {
    "raw_water": [
        RegisterDef(0, "tank_level", 1, writable=False),
        RegisterDef(1, "intake_pump_speed", 1, writable=True),
    ],
    "dosing": [
        RegisterDef(0, "ph_value", 100, writable=False),
        RegisterDef(1, "flow_rate", 10, writable=False),
        RegisterDef(2, "pump_speed", 1, writable=True),
        RegisterDef(3, "ph_setpoint", 100, writable=True),
        RegisterDef(4, "pump_state", 1, writable=True, is_bool=True),
    ],
    "filtration": [
        RegisterDef(0, "turbidity_in", 10, writable=False),
        RegisterDef(1, "turbidity_out", 10, writable=False),
        RegisterDef(2, "filter_efficiency", 1, writable=False),
    ],
    "disinfection": [
        RegisterDef(0, "chlorine_dose", 100, writable=True),
        RegisterDef(1, "pathogen_index", 1, writable=False),
    ],
    "distribution": [
        RegisterDef(0, "final_ph", 100, writable=False),
        RegisterDef(1, "final_turbidity", 10, writable=False),
        RegisterDef(2, "final_pathogen_index", 1, writable=False),
        RegisterDef(3, "distribution_flow", 10, writable=False),
    ],
}


def register_count(stage: str) -> int:
    return len(STAGE_REGISTERS[stage])


def encode_value(reg: RegisterDef, value) -> int:
    if reg.is_bool:
        return 1 if value else 0
    return round(value * reg.scale)


def decode_value(reg: RegisterDef, raw: int):
    if reg.is_bool:
        return bool(raw)
    return raw / reg.scale


def encode_state(stage: str, state: dict) -> list[int]:
    defs = STAGE_REGISTERS[stage]
    return [encode_value(reg, state[reg.name]) for reg in defs]


def decode_registers(stage: str, registers: list[int]) -> dict:
    defs = STAGE_REGISTERS[stage]
    return {reg.name: decode_value(reg, raw) for reg, raw in zip(defs, registers)}


def decode_registers_from_offset(stage: str, address: int, values: list[int]) -> dict:
    defs_by_address = {reg.address: reg for reg in STAGE_REGISTERS[stage]}
    result = {}
    for i, raw in enumerate(values):
        reg = defs_by_address.get(address + i)
        if reg is not None:
            result[reg.name] = decode_value(reg, raw)
    return result


def writable_fields(stage: str) -> set[str]:
    return {reg.name for reg in STAGE_REGISTERS[stage] if reg.writable}