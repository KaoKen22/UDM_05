import socket

# 1. Custom Exception cho câu lệnh sai

class InvalidCommandError(Exception):
    """Ngoại lệ bắn ra khi Client gửi câu lệnh không tồn tại hoặc không hợp lệ."""
    def __init__(self, command: str, message: str = "Câu lệnh không tồn tại hoặc không được hỗ trợ!"):
        self.command = command
        self.message = f"{message} (Lệnh nhận được: '{command}')"
        super().__init__(self.message)


# 2. Xử lý Exception chính (try...except handler)

def handle_exception(e: Exception) -> str:
    """
    Phân loại và bắt ngoại lệ từ khối try...except, 
    trả về thông điệp lỗi dạng chuỗi thân thiện người dùng.
    """
    # Nhóm 1: Bắt lỗi khi Client gửi câu lệnh sai
    if isinstance(e, InvalidCommandError):
        return f"[LỖI LỆNH] {e.message}"

    # Nhóm 2: Bắt lỗi try...except cơ bản khi Khởi tạo & Kết nối
    elif isinstance(e, ConnectionRefusedError):
        return "[LỖI KHỞI TẠO] Không thể kết nối. Server chưa bật hoặc sai Port."
    
    elif isinstance(e, socket.gaierror):
        return "[LỖI KHỞI TẠO] Địa chỉ IP/HOST không hợp lệ."
        
    elif isinstance(e, OSError) and e.errno == 98:  # Address already in use
        return "[LỖI KHỞI TẠO] Cổng (Port) đã được sử dụng bởi ứng dụng khác."

    # Nhóm 3: Bắt lỗi Ngắt kết nối đột ngột & Timeout
    elif isinstance(e, (ConnectionResetError, BrokenPipeError)):
        return "[LỖI NGẮT KẾT NỐI] Đối phương đã ngắt kết nối đột ngột!"
        
    elif isinstance(e, socket.timeout):
        return "[LỖI TIMEOUT] Quá thời gian chờ phản hồi từ Socket."
        
    elif isinstance(e, socket.error):
        return f"[LỖI SOCKET] Lỗi kết nối mạng: {e}"

    # Các lỗi ngoài dự tính
    else:
        return f"[LỖI KHÔNG XÁC ĐỊNH] {e}"


# 3. Hàm bổ trợ validation câu lệnh Client

def validate_command(action: str, allowed_actions: list) -> None:
    """
    Kiểm tra câu lệnh nhận từ Client. 
    Nếu câu lệnh sai hoặc không nằm trong danh sách cho phép -> Bắn InvalidCommandError.
    """
    if not action or action not in allowed_actions:
        raise InvalidCommandError(command=action)
