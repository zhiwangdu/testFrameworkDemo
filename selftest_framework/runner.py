from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

from .cases import opengemini_rw_smoke
from .config import RuntimeConfig, load_runtime_config
from .env_init import initialize_environment


CaseFn = Callable[[RuntimeConfig], dict[str, Any]]

CASES: dict[str, CaseFn] = {
    "opengemini_rw_smoke": opengemini_rw_smoke.run,
}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_case(config: RuntimeConfig) -> dict[str, Any]:
    if config.case_name not in CASES:
        available = ", ".join(sorted(CASES))
        raise RuntimeError(f"unknown case {config.case_name}; available: {available}")

    initialize_environment(config)
    details = CASES[config.case_name](config)
    return {
        "status": "OK",
        "caseName": config.case_name,
        "instanceId": config.instance_id,
        "endpoint": config.endpoint,
        "details": details,
    }


def main() -> int:
    try:
        config = load_runtime_config()
        result = run_case(config)
        write_json(config.artifacts_dir / "test-result.json", result)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as exc:
        artifacts_dir = None
        try:
            artifacts_dir = load_runtime_config().artifacts_dir
        except Exception:
            artifacts_dir = Path("/tmp/test-framework-demo-artifacts")

        result = {
            "status": "FAILED",
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }
        write_json(artifacts_dir / "test-result.json", result)
        print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
