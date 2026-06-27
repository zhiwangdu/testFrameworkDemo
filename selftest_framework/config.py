from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeConfig:
    case_name: str
    instance_id: str
    endpoint: str
    artifacts_dir: Path


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"missing required env {name}")
    return value


def resolve_endpoint() -> str:
    endpoint = os.environ.get("DEVSELFTEST_PARAM_ENDPOINT", "").strip()
    if endpoint:
        return endpoint.rstrip("/")

    host = os.environ.get("DEVSELFTEST_HOST", "").strip()
    port = os.environ.get("DEVSELFTEST_PORT", "").strip()
    if host and port:
        return f"http://{host}:{port}".rstrip("/")

    raise RuntimeError("missing DEVSELFTEST_PARAM_ENDPOINT or DEVSELFTEST_HOST/PORT")


def resolve_artifacts_dir() -> Path:
    explicit = os.environ.get("SELFTEST_ARTIFACTS_DIR", "").strip()
    if explicit:
        return Path(explicit)

    mounted = Path("/workspace/artifacts")
    if mounted.exists():
        return mounted

    return Path(os.environ.get("DEVSELFTEST_ARTIFACTS_DIR", "/workspace/artifacts"))


def load_runtime_config() -> RuntimeConfig:
    return RuntimeConfig(
        case_name=required_env("DEVSELFTEST_PARAM_CASE_NAME"),
        instance_id=required_env("DEVSELFTEST_PARAM_INSTANCE_ID"),
        endpoint=resolve_endpoint(),
        artifacts_dir=resolve_artifacts_dir(),
    )
