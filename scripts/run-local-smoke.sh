#!/usr/bin/env sh
set -eu

IMAGE="${IMAGE:-test-framework-demo:dev}"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-/tmp/test-framework-demo-artifacts}"
ENDPOINT="${ENDPOINT:-http://host.docker.internal:18086}"

docker build -t "$IMAGE" .
rm -rf "$ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

docker run --rm \
  -e DEVSELFTEST_PARAM_CASE_NAME=opengemini_rw_smoke \
  -e DEVSELFTEST_PARAM_INSTANCE_ID=local-demo \
  -e DEVSELFTEST_PARAM_ENDPOINT="$ENDPOINT" \
  -e SELFTEST_ARTIFACTS_DIR=/workspace/artifacts \
  -v "$ARTIFACTS_DIR:/workspace/artifacts:rw" \
  "$IMAGE"

cat "$ARTIFACTS_DIR/test-result.json"
