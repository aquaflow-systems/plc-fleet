import httpx

DEFAULT_BASE_URL = "http://plant-sim:8000"


class PlantSimClient:
    def __init__(self, base_url: str = DEFAULT_BASE_URL, timeout: float = 2.0):
        self._client = httpx.Client(base_url=base_url, timeout=timeout)

    def get_state(self, stage: str) -> dict:
        response = self._client.get(f"/state/{stage}")
        response.raise_for_status()
        return response.json()

    def actuate(self, stage: str, values: dict) -> dict:
        response = self._client.post(f"/actuate/{stage}", json={"values": values})
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()
