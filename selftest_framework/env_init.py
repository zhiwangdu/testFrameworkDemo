from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import RuntimeConfig


def initialize_environment(config: RuntimeConfig) -> dict[str, str]:
    config.artifacts_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "caseName": config.case_name,
        "instanceId": config.instance_id,
        "endpoint": config.endpoint,
    }
    (config.artifacts_dir / "test-env.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-name", required=True)
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--artifacts-dir", default="/workspace/artifacts")
    args = parser.parse_args()
    initialize_environment(
        RuntimeConfig(
            case_name=args.case_name,
            instance_id=args.instance_id,
            endpoint=args.endpoint.rstrip("/"),
            artifacts_dir=Path(args.artifacts_dir),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
