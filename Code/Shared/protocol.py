import json

# Định nghĩa các loại hành động
ACTION_EXECUTE = "EXECUTE"
ACTION_DISCONNECT = "DISCONNECT"

# Định nghĩa trạng thái phản hồi
STATUS_SUCCESS = "SUCCESS"
STATUS_ERROR = "ERROR"

def build_request(action: str, command: str = "") -> str:
    """Đóng gói yêu cầu từ Client gửi sang Server (JSON)"""
    return json.dumps({
        "action": action,
        "command": command
    })

def parse_request(data_str: str) -> dict:
    """Giải mã tin nhắn Request mà Server nhận được"""
    try:
        return json.loads(data_str)
    except Exception:
        return {"action": "UNKNOWN", "command": ""}

def build_response(status: str, output: str = "", message: str = "") -> str:
    """Đóng gói phản hồi từ Server gửi về Client (JSON)"""
    return json.dumps({
        "status": status,
        "output": output,
        "message": message
    })

def parse_response(data_str: str) -> dict:
    """Giải mã tin nhắn Response mà Client nhận được"""
    try:
        return json.loads(data_str)
    except Exception:
        return {"status": STATUS_ERROR, "output": "", "message": "Dữ liệu không hợp lệ"}


    