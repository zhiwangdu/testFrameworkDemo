import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from selftest_framework.config import load_runtime_config, resolve_endpoint
from selftest_framework.env_init import initialize_environment


class ConfigTests(unittest.TestCase):
    def test_load_runtime_config_from_toolhub_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {
                "DEVSELFTEST_PARAM_CASE_NAME": "opengemini_rw_smoke",
                "DEVSELFTEST_PARAM_INSTANCE_ID": "inst-1",
                "DEVSELFTEST_PARAM_ENDPOINT": "http://example.test:8086",
                "SELFTEST_ARTIFACTS_DIR": tmp,
            }
            with patch.dict(os.environ, env, clear=True):
                config = load_runtime_config()
            self.assertEqual(config.case_name, "opengemini_rw_smoke")
            self.assertEqual(config.instance_id, "inst-1")
            self.assertEqual(config.endpoint, "http://example.test:8086")
            self.assertEqual(config.artifacts_dir, Path(tmp))

    def test_endpoint_falls_back_to_devselftest_host_port(self) -> None:
        with patch.dict(
            os.environ,
            {"DEVSELFTEST_HOST": "127.0.0.1", "DEVSELFTEST_PORT": "8086"},
            clear=True,
        ):
            self.assertEqual(resolve_endpoint(), "http://127.0.0.1:8086")

    def test_initialize_environment_writes_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {
                "DEVSELFTEST_PARAM_CASE_NAME": "opengemini_rw_smoke",
                "DEVSELFTEST_PARAM_INSTANCE_ID": "inst-1",
                "DEVSELFTEST_PARAM_ENDPOINT": "http://example.test:8086",
                "SELFTEST_ARTIFACTS_DIR": tmp,
            }
            with patch.dict(os.environ, env, clear=True):
                config = load_runtime_config()
            initialize_environment(config)
            self.assertTrue((Path(tmp) / "test-env.json").exists())


if __name__ == "__main__":
    unittest.main()
