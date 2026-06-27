from __future__ import annotations

import time
from typing import Any

import requests

from ..config import RuntimeConfig


def check_query_response(payload: dict[str, Any]) -> None:
    for result in payload.get("results", []):
        if "error" in result:
            raise RuntimeError(result["error"])


def run(config: RuntimeConfig) -> dict[str, Any]:
    endpoint = config.endpoint.rstrip("/")
    db_name = f"toolhub_selftest_{int(time.time() * 1000)}"
    measurement = "rw_smoke"
    timestamp = time.time_ns()
    line = f"{measurement},case={config.case_name} value=1i {timestamp}"

    create = requests.post(
        f"{endpoint}/query",
        params={"q": f"CREATE DATABASE {db_name}"},
        timeout=10,
    )
    create.raise_for_status()
    check_query_response(create.json())

    write = requests.post(
        f"{endpoint}/write",
        params={"db": db_name},
        data=line,
        timeout=10,
    )
    write.raise_for_status()

    last_payload: dict[str, Any] | None = None
    for _ in range(10):
        select = requests.get(
            f"{endpoint}/query",
            params={"db": db_name, "q": f"SELECT value FROM {measurement}"},
            timeout=10,
        )
        select.raise_for_status()
        payload = select.json()
        check_query_response(payload)
        last_payload = payload
        for result in payload.get("results", []):
            for series in result.get("series", []):
                values = series.get("values") or []
                if values:
                    return {
                        "database": db_name,
                        "measurement": measurement,
                        "writtenLine": line,
                        "queryValues": values,
                    }
        time.sleep(0.5)

    raise RuntimeError(f"query did not return the written point: {last_payload}")
