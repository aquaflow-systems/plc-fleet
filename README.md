# plc-fleet

Emulated PLCs for all 5 treatment stages. Each PLC process polls `plant-sim`'s
internal API for sensor values and actuator state, keeps a Modbus register table
in sync with them, and exposes that table over real Modbus to anything on
`control-net` -- exactly like a real PLC would on the wire.

## Stages and protocol

| Stage | Protocol |
|---|---|
| raw_water | Modbus Security (TLS) |
| dosing | Modbus/TCP |
| filtration | Modbus Security (TLS) |
| disinfection | Modbus Security (TLS) |
| distribution | Modbus Security (TLS) |

Register addresses and scaling: see `AquaFlow-Systems/plant-spec/register-map.md`.

## Running one stage standalone

```bash
pip install -r requirements.txt
python -m src.main --stage dosing --no-tls
```

For a TLS-secured stage, point `--certs` at the output of
`plant-spec/certs/generate-certs.sh`:

```bash
python -m src.main --stage filtration --certs ../plant-spec/certs/out
```

Requires `plant-sim` to already be running and reachable (see
`AquaFlow-Systems/plant-spec/network-plan.md` for the expected address).

## Tests

```bash
pytest
```