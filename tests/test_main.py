import subprocess
import sys
import shutil

def test_cli_help_runs():
    # Run as module
    result = subprocess.run(
        [sys.executable, "-m", "flyfield.cli", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()


def test_installed_entry_point_works():
    # Ensure console script "flyfield" exists in PATH
    exe = shutil.which("flyfield")
    assert exe is not None, "flyfield entry point not found in PATH"

    result = subprocess.run(
        [exe, "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
