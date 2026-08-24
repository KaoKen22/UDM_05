import json

# ==========================================
# 1. ĐỊNH NGHĨA CÁC HẰNG SỐ (CONSTANTS)
# ==========================================
ACTION_EXECUTE = "EXECUTE"
ACTION_LIST_DIR = "LIST_DIR"
ACTION_DISCONNECT = "DISCONNECT"

STATUS_SUCCESS = "SUCCESS"
STATUS_ERROR = "ERROR"


# ==========================================
# 2. CÁC HÀM XỬ LÝ DỮ LIỆU (FUNCTIONS)
# ==========================================

def build_request(action: str, payload: dict = None) -> str:
    """Đóng gói yêu cầu từ Client thành chuỗi JSON"""
    if payload is None:
        payload = {}
    return json.dumps({"action": action, "payload": payload}, ensure_ascii=False)


def build_execute_request(command: str) -> str:
    """Hàm tiện ích: Đóng gói request chạy lệnh CMD (ACTION_EXECUTE)"""
    return build_request(ACTION_EXECUTE, {"command": command})


def build_list_dir_request(path: str = ".") -> str:
    """Hàm tiện ích Tuần 2: Đóng gói request xem danh sách thư mục (ACTION_LIST_DIR)"""
    return build_request(ACTION_LIST_DIR, {"path": path})


def parse_request(data_str: str) -> dict:
    """Giải mã chuỗi JSON yêu cầu từ Client thành Dictionary"""
    try:
        data = json.loads(data_str)
        return {
            "action": data.get("action", "UNKNOWN"),
            "payload": data.get("payload", {})
        }
    except Exception:
        return {"action": "UNKNOWN", "payload": {}}


def build_response(status: str, output: str = "", message: str = "") -> str:
    """Đóng gói phản hồi từ Server trả về Client thành chuỗi JSON"""
    response_data = {
        "status": status,
        "output": output,
        "message": message
    }
    return json.dumps(response_data, ensure_ascii=False)


def parse_response(data_str: str) -> dict:
    """Giải mã chuỗi JSON phản hồi từ Server thành Dictionary"""
    try:
        return json.loads(data_str)
    except Exception:
        return {
            "status": STATUS_ERROR,
            "output": "",
            "message": "Dữ liệu JSON không hợp lệ"
        }