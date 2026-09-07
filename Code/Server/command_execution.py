import subprocess
import shlex
import shutil
import platform
import os
import time

try:
    import psutil
except Exception:
    psutil = None

ALLOWED_COMMANDS = {
    "ping",
    "ipconfig",
    "hostname",
    "whoami",
    "dir",
    "echo",
}

FORBIDDEN_CHARS = [";", "&&", "||", "|", "`", "$", ">", "<"]

WINDOWS_BUILTINS = {"dir", "echo"}

def validate_command(user_input: str):
    if not user_input or not user_input.strip():
        return False, "Lệnh rỗng.", []

    for char in FORBIDDEN_CHARS:
        if char in user_input:
            return False, f"Phát hiện kí tự cấm: {char}", []

    try:
        tokens = shlex.split(user_input)
    except Exception as e:
        return False, f"Lỗi cú pháp: {e}", []

    if not tokens:
        return False, "Lệnh không hợp lệ.", []

    if tokens[0].lower() not in ALLOWED_COMMANDS:
        return False, f"Lệnh '{tokens[0]}' không được phép.", []

    return True, "", tokens

def execute_command(user_input: str) -> dict:
    is_valid, err_msg, tokens = validate_command(user_input)
    if not is_valid:
        return {
            "exit_code": 1,
            "output": "",
            "error": err_msg
        }
    if platform.system().lower().startswith("win"):
        cmd0 = tokens[0].lower()
        if cmd0 in WINDOWS_BUILTINS:
            tokens = ["cmd", "/c"] + tokens

    if tokens and tokens[0].lower() != "cmd":
        if shutil.which(tokens[0]) is None:
            return {"exit_code": 1, "output": "", "error": f"Không tìm thấy thực thi: {tokens[0]}"}

    return run_real_command(tokens, timeout=15)


def run_real_command(tokens, timeout=15) -> dict:
    if isinstance(tokens, str):
        try:
            tokens = shlex.split(tokens)
        except Exception as e:
            return {"exit_code": 1, "output": "", "error": f"Lỗi cú pháp: {e}"}

    try:
        output = subprocess.check_output(
            tokens,
            stderr=subprocess.STDOUT,
            timeout=timeout,
            shell=False,
            text=True
        )
        return {"exit_code": 0, "output": output.strip(), "error": ""}
    except subprocess.CalledProcessError as e:
        out = e.output if isinstance(e.output, str) else (e.output.decode() if e.output else "")
        return {"exit_code": e.returncode, "output": out.strip(), "error": f"Lệnh thất bại với mã {e.returncode}"}
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "output": "", "error": f"Thực thi lệnh vượt quá thời gian cho phép ({timeout}s)."}
    except FileNotFoundError:
        return {"exit_code": -1, "output": "", "error": f"Lệnh '{tokens[0]}' không tồn tại hoặc không hỗ trợ khi shell=False."}
    except Exception as e:
        return {"exit_code": -1, "output": "", "error": str(e)}


def list_files(path: str = ".") -> dict:
    try:
        items = os.listdir(path)
        return {"success": True, "files": items}
    except Exception as e:
        return {"success": False, "files": [], "error": str(e)}


def kill_process(pid, force: bool = False) -> dict:
    try:
        pid_int = int(pid)
    except Exception:
        return {"success": False, "error": "PID không hợp lệ"}

    if psutil:
        try:
            proc = psutil.Process(pid_int)
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                if force:
                    proc.kill()
            return {"success": True, "message": "Đã dừng tiến trình"}
        except psutil.NoSuchProcess:
            return {"success": False, "error": "Không tìm thấy tiến trình"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    if platform.system().lower().startswith("win"):
        cmd = ["taskkill", "/PID", str(pid_int)]
        if force:
            cmd.append("/F")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return {"success": True, "message": res.stdout.strip()}
            else:
                return {"success": False, "error": res.stderr.strip() or res.stdout.strip()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    try:
        os.kill(pid_int, 15)
        time.sleep(0.1)
        return {"success": True, "message": "Đã gửi tín hiệu SIGTERM"}
    except ProcessLookupError:
        return {"success": False, "error": "Không tìm thấy tiến trình"}
    except Exception as e:
        return {"success": False, "error": str(e)}
