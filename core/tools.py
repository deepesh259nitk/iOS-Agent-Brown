from pathlib import Path
import subprocess

WORKSPACE = Path("./workspace")

def read_file(path):

    full_path = WORKSPACE / path

    if not full_path.exists():
        return "File does not exist"

    return full_path.read_text()


def write_file(path, content):

    full_path = WORKSPACE / path

    full_path.parent.mkdir(parents=True, exist_ok=True)

    full_path.write_text(content)

    return "File written successfully"


def list_files(path="."):

    full_path = WORKSPACE / path

    files = []

    for p in full_path.rglob("*"):
        if p.is_file():
            files.append(str(p.relative_to(WORKSPACE)))

    return "\n".join(files)


def run_command(cmd):

    allowed_commands = [
        "xcodebuild",
        "swift",
        "git",
        "ls",
        "pwd"
    ]

    # SAFETY CHECK
    if not any(cmd.startswith(c) for c in allowed_commands):
        return "Command not allowed"

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=WORKSPACE
    )

    return f"""
EXIT CODE:
{result.returncode}

STDOUT:
{result.stdout}

STDERR:
{result.stderr}
"""


TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "run_command": run_command,
}