import argparse
import logging

from src.plc import Plc

DEFAULT_PLANT_SIM_URL = "http://plant-sim:8000"
DEFAULT_PORT = 502


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one stage's emulated PLC")
    parser.add_argument("--stage", required=True, help="stage name, e.g. dosing")
    parser.add_argument(
        "--no-tls",
        action="store_true",
        help="run plaintext Modbus/TCP instead of Modbus Security",
    )
    parser.add_argument(
        "--certs", default=None, help="path to certs directory (required unless --no-tls)"
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--plant-sim-url", default=DEFAULT_PLANT_SIM_URL)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = parse_args()

    if not args.no_tls and not args.certs:
        raise SystemExit("--certs is required unless --no-tls is set")

    plc = Plc(
        stage=args.stage,
        plant_sim_url=args.plant_sim_url,
        port=args.port,
        use_tls=not args.no_tls,
        certs_dir=args.certs,
    )
    plc.start()


if __name__ == "__main__":
    main()