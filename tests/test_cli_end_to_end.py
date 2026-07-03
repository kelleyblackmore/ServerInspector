import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


def test_cli_run_end_to_end(tmp_path):
    project_root = Path(__file__).resolve().parents[1]

    data_dir = tmp_path / "artifacts"
    data_dir.mkdir()
    log_file = data_dir / "application.log"
    message = "E2E COMMAND OUTPUT"
    log_file.write_text("Log start\n" + message + "\n")

    config_payload = {"service": {"enabled": True, "port": 8080}}
    json_config_path = tmp_path / "service.json"
    json_config_path.write_text(json.dumps(config_payload))

    variables = {
        "DATA_DIR": str(data_dir),
        "LOG_FILE": str(log_file),
        "PYTHON_BIN": sys.executable,
        "MESSAGE": message,
        "CONFIG_FILE": str(json_config_path),
    }

    config = {
        "title": "CLI end-to-end validation",
        "description": "Ensures the CLI orchestrates a full inspection run.",
        "environment": {"variables": variables},
        "tests": [
            {
                "name": "Directory exists",
                "type": "file",
                "path": "{{ DATA_DIR }}",
                "exists": True,
                "type": "directory",
            },
            {
                "name": "Log file contents",
                "type": "file",
                "path": "{{ LOG_FILE }}",
                "exists": True,
                "content": "{{ MESSAGE }}",
            },
            {
                "name": "Python command execution",
                "type": "command",
                "command": "{{ PYTHON_BIN }} -c \"print('{{ MESSAGE }}')\"",
                "exit_status": 0,
                "stdout": {"contains": "{{ MESSAGE }}"},
            },
            {
                "name": "JSON config inspection",
                "type": "config",
                "path": "{{ CONFIG_FILE }}",
                "format": "json",
                "has_key": "service.enabled",
                "has_value": {
                    "service.enabled": True,
                    "service.port": 8080,
                },
            },
        ],
    }

    config_path = tmp_path / "scenario.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False))

    output_file = tmp_path / "results.json"

    env = os.environ.copy()
    pythonpath = str(project_root / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        pythonpath
        if not existing_pythonpath
        else f"{pythonpath}{os.pathsep}{existing_pythonpath}"
    )

    command = [
        sys.executable,
        "-m",
        "serverinspect.cli",
        "run",
        str(config_path),
        "--output-format",
        "json",
        "--output-file",
        str(output_file),
    ]

    completed = subprocess.run(
        command,
        cwd=project_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert (
        completed.returncode == 0
    ), f"CLI exited with {completed.returncode}\nstdout: {completed.stdout}\nstderr: {completed.stderr}"
    assert "All 4 tests passed!" in completed.stdout
    assert completed.stderr == ""

    assert output_file.exists(), "CLI did not produce the JSON output file"
    results = json.loads(output_file.read_text())

    assert results["summary"]["total"] == 4
    assert results["summary"]["passed"] == 4
    assert results["summary"]["failed"] == 0

    assert "system_info" in results
    assert results["system_info"].get("hostname")

    test_names = [test["name"] for test in results["tests"]]
    assert test_names == [
        "Directory exists",
        "Log file contents",
        "Python command execution",
        "JSON config inspection",
    ]

    log_test = next(test for test in results["tests"] if test["name"] == "Log file contents")
    assert log_test["details"]["path"] == str(log_file)
    assert log_test["details"]["has_content"] is True

    command_test = next(
        test for test in results["tests"] if test["name"] == "Python command execution"
    )
    assert command_test["details"]["expected_stdout_contains"] == message
    assert message in command_test["details"]["stdout"]

    config_test = next(
        test for test in results["tests"] if test["name"] == "JSON config inspection"
    )
    assert config_test["details"]["format"] == "json"
    assert config_test["details"]["key_value"].lower() == "true"
    assert config_test["details"]["value_match_service.enabled"] is True
    assert config_test["details"]["value_match_service.port"] is True
