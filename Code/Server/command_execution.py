import subprocess
import shlex

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


if __name__ == "__main__":
    print("Test 1 (hostname):", execute_command("hostname"))
    print("Test 2 (ping 127.0.0.1):", execute_command("ping 127.0.0.1"))
    print("Test 3 (Lỗi cấm nối lệnh):", execute_command("ipconfig && whoami"))