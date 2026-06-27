# testFrameworkDemo

Minimal Python test framework demo for LocalToolHub `dev_selftest.run_tests`.

The framework is designed to run inside a Docker image. ToolHub passes non-secret runtime
parameters as environment variables:

```text
DEVSELFTEST_PARAM_CASE_NAME=opengemini_rw_smoke
DEVSELFTEST_PARAM_INSTANCE_ID=<instance id from internal skill>
DEVSELFTEST_PARAM_ENDPOINT=http://host:8086
```

Credentials must not be passed through these variables. ToolHub injects them via Docker
`--env KEY=VALUE`, so values can be visible in host process arguments while the container starts.

## Layout

```text
selftest_framework/
  runner.py                  # entrypoint
  env_init.py                # writes test-env.json
  cases/opengemini_rw_smoke.py
scripts/
  mock_influx_api.py         # local Influx/openGemini-compatible API stub
  run-local-smoke.sh         # build image and run the demo against the stub
tests/
  test_config.py
Dockerfile
requirements.txt
```

## Build

```bash
docker build -t test-framework-demo:dev .
```

## Run Locally

Terminal 1:

```bash
python3 scripts/mock_influx_api.py --host 127.0.0.1 --port 18086
```

Terminal 2:

```bash
mkdir -p /tmp/test-framework-demo-artifacts
docker run --rm --network host \
  -e DEVSELFTEST_PARAM_CASE_NAME=opengemini_rw_smoke \
  -e DEVSELFTEST_PARAM_INSTANCE_ID=local-demo \
  -e DEVSELFTEST_PARAM_ENDPOINT=http://127.0.0.1:18086 \
  -e SELFTEST_ARTIFACTS_DIR=/workspace/artifacts \
  -v /tmp/test-framework-demo-artifacts:/workspace/artifacts:rw \
  test-framework-demo:dev
```

On Docker Desktop for Mac, replace the endpoint with `http://host.docker.internal:18086` when
running the container outside `--network host` semantics.

The runner writes:

```text
test-env.json
test-result.json
```

## ToolHub Suite Example

```yaml
remote_execution:
  commands:
    cloud_opengemini_case:
      enabled: true
      argv: ["python", "-m", "selftest_framework.runner"]
      timeout_seconds: 300

dev_selftest:
  test_suites:
    cloud_opengemini_case:
      command: cloud_opengemini_case
      timeout_seconds: 300
      docker:
        image: "test-framework-demo:dev"
        network: "host"
        workdir: "/workspace/source"
        volumes:
          - "${DEVSELFTEST_SOURCE_DIR}:/workspace/source:ro"
          - "${DEVSELFTEST_ARTIFACTS_DIR}:/workspace/artifacts:rw"
```

External/internal skills should create the cloud openGemini/influxdb instance, then call
`run_tests` with:

```json
{
  "runId": "devselftest_...",
  "testSuite": "cloud_opengemini_case",
  "testParams": {
    "caseName": "opengemini_rw_smoke",
    "instanceId": "demo-instance",
    "endpoint": "http://host:8086"
  }
}
```
