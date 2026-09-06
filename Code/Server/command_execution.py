import subprocess
import shlex
import shutil
import platform

ALLOWED_COMMANDS = {
    "ping",
    "ipconfig",
    "ifconfig",
    "hostname",
    "whoami",
    "dir",
    "ls",
    "echo"
}

FORBIDDEN_CHARS = [";", "&&", "||", "|", "`", "$", ">", "<"]

WINDOWS_BUILTINS = {"dir", "echo"}

def validate_command(user_input: str):
    if not user_input or not user_input.strip():
        return False, "Command is empty.", []

    for char in FORBIDDEN_CHARS:
        if char in user_input:
            return False, f"Forbidden character detected: {char}", []

    try:
        tokens = shlex.split(user_input)
    except Exception as e:
        return False, f"Syntax error: {e}", []

    if not tokens:
        return False, "Invalid command.", []

    if tokens[0].lower() not in ALLOWED_COMMANDS:
        return False, f"Command '{tokens[0]}' is not allowed.", []

    return True, "", tokens

def execute_command(user_input: str) -> dict:
    is_valid, err_msg, tokens = validate_command(user_input)
    if not is_valid:
        return {
            "exit_code": 1,
            "output": "",
            "error": err_msg
        }

    try:
        if platform.system().lower().startswith("win"):
            cmd0 = tokens[0].lower()
            if cmd0 == "ls":
                tokens = ["cmd", "/c", "dir"] + tokens[1:]
            elif cmd0 in WINDOWS_BUILTINS:
                tokens = ["cmd", "/c"] + tokens

    # Check executable exists (skip 'cmd')
        if tokens and tokens[0].lower() != "cmd":
            if shutil.which(tokens[0]) is None:
                return {"exit_code": 1, "output": "", "error": f"Executable not found: {tokens[0]}"}

        result = subprocess.run(
            tokens,
            capture_output=True,
            text=True,
            timeout=15,
            shell=False
        )
        return {
            "exit_code": result.returncode,
            "output": result.stdout.strip(),
            "error": result.stderr.strip()
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": -1,
            "output": "",
            "error": "Command execution timed out (15s)."
        }
    except FileNotFoundError:
        return {
            "exit_code": -1,
            "output": "",
            "error": f"Lệnh '{tokens[0]}' không tồn tại hoặc không hỗ trợ khi shell=False."
        }
    except Exception as e:
        return {
            "exit_code": -1,
            "output": "",
            "error": str(e)
        }
