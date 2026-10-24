import logging
import threading
import time
from pathlib import Path

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext, ModbusSlaveContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartTcpServer, StartTlsServer

from src.plant_sim_client import PlantSimClient
from src.registers import (
    STAGE_REGISTERS,
    decode_registers_from_offset,
    encode_state,
    register_count,
    writable_fields,
)

logger = logging.getLogger(__name__)

POLL_SECONDS = 1.0


class WatchedDataBlock(ModbusSequentialDataBlock):

    def __init__(self, address, values, on_write):
        super().__init__(address, values)
        self._on_write = on_write

    def setValues(self, address, values):
        super().setValues(address, values)
        self._on_write(address, values)

    def refresh(self, address, values):
        super().setValues(address, values)


class Plc:
    def __init__(
        self,
        stage: str,
        plant_sim_url: str,
        port: int = 502,
        use_tls: bool = False,
        certs_dir: str | None = None,
    ):
        if stage not in STAGE_REGISTERS:
            raise ValueError(f"unknown stage '{stage}'")

        self.stage = stage
        self.port = port
        self.use_tls = use_tls
        self.certs_dir = certs_dir
        self.client = PlantSimClient(base_url=plant_sim_url)
        self._writable = writable_fields(stage)

        initial = [0] * register_count(stage)
        self.block = WatchedDataBlock(0, initial, on_write=self._handle_write)

        slave_context = ModbusSlaveContext(hr=self.block, zero_mode=True)
        self.context = ModbusServerContext(slaves=slave_context, single=True)

        self._stop_event = threading.Event()

    def _handle_write(self, address: int, values: list[int]) -> None:
        changes = decode_registers_from_offset(self.stage, address, values)
        to_send = {k: v for k, v in changes.items() if k in self._writable}
        if not to_send:
            return
        try:
            updated = self.client.actuate(self.stage, to_send)
            self._apply_state(updated)
        except Exception:
            logger.exception("failed to relay write to plant-sim for stage %s", self.stage)

    def _apply_state(self, state: dict) -> None:
        values = encode_state(self.stage, state)
        self.block.refresh(0, values)

    def _poll_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                state = self.client.get_state(self.stage)
                self._apply_state(state)
            except Exception:
                logger.exception("failed to poll plant-sim for stage %s", self.stage)
            time.sleep(POLL_SECONDS)

    def start(self) -> None:
        poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        poll_thread.start()

        identity = ModbusDeviceIdentification()
        identity.VendorName = "AquaFlow Systems"
        identity.ProductName = f"PLC - {self.stage}"

        logger.info(
            "starting Modbus server for stage '%s' on port %s (tls=%s)",
            self.stage,
            self.port,
            self.use_tls,
        )

        if self.use_tls:
            cert_base = f"plc-{self.stage.replace('_', '-')}"
            certs_path = Path(self.certs_dir)
            StartTlsServer(
                context=self.context,
                identity=identity,
                address=("0.0.0.0", self.port),
                certfile=str(certs_path / f"{cert_base}.crt"),
                keyfile=str(certs_path / f"{cert_base}.key"),
                ca=str(certs_path / "ca.crt"),
            )
        else:
            StartTcpServer(context=self.context, identity=identity, address=("0.0.0.0", self.port))
