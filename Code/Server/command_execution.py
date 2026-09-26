import os
import shlex
import shutil
import subprocess
import threading


ALLOWED_COMMANDS = {
    "ping",
    "ipconfig",
    "hostname",
    "whoami",
    "dir",
    "echo"
}

FORBIDDEN_CHARS = [
    ";",
    "&&",
    "||",
    "|",
    "`",
    "$",
    ">",
    "<"
]

WINDOWS_BUILTINS = {
    "dir",
    "echo"
}


def validate_command(command):
    if not isinstance(command, str) or not command.strip():
        return False, "Lệnh không được để trống.", None

    for char in FORBIDDEN_CHARS:
        if char in command:
            return (
                False,
                f"Phát hiện ký tự/chuỗi bị cấm: {char}",
                None
            )

    try:
        tokens = shlex.split(
            command,
            posix=False
        )
    except ValueError as error:
        return False, f"Lệnh không hợp lệ: {error}", None

    if not tokens:
        return False, "Lệnh không được để trống.", None

    executable = tokens[0].strip('"').lower()

    if executable not in ALLOWED_COMMANDS:
        return (
            False,
            f"Lệnh '{executable}' không nằm trong danh sách cho phép.",
            None
        )

    return True, "", tokens


def _build_process_args(tokens):
    executable = tokens[0].strip('"').lower()

    if executable in WINDOWS_BUILTINS:
        return [
            "cmd",
            "/c",
            subprocess.list2cmdline(tokens)
        ]

    if shutil.which(executable) is None:
        raise FileNotFoundError(
            f"Không tìm thấy lệnh '{executable}' trên hệ thống."
        )

    return tokens


def stop_process(process):
    """
    Chỉ dừng process do chính Server tạo cho command hiện tại.
    """
    if process is None:
        return False

    if process.poll() is not None:
        return False

    try:
        if os.name == "nt":
            subprocess.run(
                [
                    "taskkill",
                    "/PID",
                    str(process.pid),
                    "/T",
                    "/F"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        else:
            process.terminate()

        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()

        return True

    except Exception:
        try:
            process.kill()
            return True
        except Exception:
            return False


def execute_command(
    command,
    timeout=15,
    process_callback=None,
    stop_event=None
):
    valid, error_message, tokens = validate_command(command)

    if not valid:
        return {
            "exit_code": -1,
            "output": "",
            "error": error_message,
            "stopped": False,
            "timed_out": False
        }

    if stop_event is None:
        stop_event = threading.Event()

    process = None

    try:
        process_args = _build_process_args(tokens)

        process = subprocess.Popen(
            process_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False
        )

        if process_callback is not None:
            process_callback(process)

        if stop_event.is_set():
            stop_process(process)

        try:
            output, error = process.communicate(
                timeout=timeout
            )

        except subprocess.TimeoutExpired:
            stop_process(process)

            try:
                output, error = process.communicate(
                    timeout=2
                )
            except Exception:
                output, error = "", ""

            return {
                "exit_code": -1,
                "output": output or "",
                "error": (
                    f"Thực thi lệnh vượt quá thời gian cho phép "
                    f"({timeout}s)."
                ),
                "stopped": False,
                "timed_out": True
            }

        if stop_event.is_set():
            return {
                "exit_code": -2,
                "output": output or "",
                "error": "",
                "stopped": True,
                "timed_out": False
            }

        return {
            "exit_code": process.returncode,
            "output": output or "",
            "error": error or "",
            "stopped": False,
            "timed_out": False
        }

    except Exception as error:
        return {
            "exit_code": -1,
            "output": "",
            "error": str(error),
            "stopped": stop_event.is_set(),
            "timed_out": False
        }
