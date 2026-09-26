import json

ACTION_EXECUTE = "EXECUTE"
ACTION_LIST_DIR = "LIST_DIR"
ACTION_STOP = "STOP"
ACTION_DISCONNECT = "DISCONNECT"

STATUS_SUCCESS = "SUCCESS"
STATUS_ERROR = "ERROR"


def build_request(action, payload=None):
    message = {
        "action": action,
        "payload": payload if payload is not None else {}
    }
    return json.dumps(message, ensure_ascii=False) + "\n"


def build_execute_request(command):
    return build_request(ACTION_EXECUTE, {"command": command})


def build_list_dir_request(path):
    return build_request(ACTION_LIST_DIR, {"path": path})


def build_stop_request():
    return build_request(ACTION_STOP)


def parse_request(data_str):
    try:
        data = json.loads(data_str)
        if not isinstance(data, dict):
            raise ValueError("Request phải là JSON object.")

        action = data.get("action")
        payload = data.get("payload", {})

        if not isinstance(action, str) or not action:
            raise ValueError("Thiếu action hợp lệ.")

        if not isinstance(payload, dict):
            raise ValueError("payload phải là JSON object.")

        return {
            "action": action,
            "payload": payload
        }
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        return {
            "action": "UNKNOWN",
            "payload": {},
            "parse_error": str(error)
        }


def build_response(status, output="", message="", error="", exit_code=None):
    response = {
        "status": status,
        "output": output,
        "message": message,
        "error": error,
        "exit_code": exit_code
    }
    return json.dumps(response, ensure_ascii=False) + "\n"


def parse_response(data_str):
    try:
        data = json.loads(data_str)
        if not isinstance(data, dict):
            raise ValueError("Response phải là JSON object.")

        return {
            "status": data.get("status", STATUS_ERROR),
            "output": data.get("output", ""),
            "message": data.get("message", ""),
            "error": data.get("error", ""),
            "exit_code": data.get("exit_code", None)
        }
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        return {
            "status": STATUS_ERROR,
            "output": "",
            "message": "Response không hợp lệ.",
            "error": str(error),
            "exit_code": None
        }
