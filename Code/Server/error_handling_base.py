import socket

#Bắt lỗi khi khởi tạo và lắng nghe kết nối Server (bind, listen).
def safe_bind_and_listen(sock: socket.socket, host: str, port: int, backlog: int = 5) -> bool:
    try:
        sock.bind((host, port))
        sock.listen(backlog)
        return True
    except socket.gaierror:
        print("[ERROR] Địa chỉ IP/HOST không hợp lệ.")
    except OSError as e:
        print(f"[ERROR] Cổng Port {port} đã được sử dụng hoặc lỗi hệ thống: {e}")
    except socket.error as e:
        print(f"[ERROR] Lỗi khởi tạo Server Socket: {e}")
    return False

#Bắt lỗi khi Client kết nối tới Server (connect).
def safe_connect(sock: socket.socket, host: str, port: int) -> bool:
    try:
        sock.connect((host, port))
        return True
    except ConnectionRefusedError:
        print("[ERROR] Kết nối bị từ chối. Server chưa bật hoặc sai Port.")
    except socket.gaierror:
        print("[ERROR] Địa chỉ IP/HOST không hợp lệ.")
    except socket.timeout:
        print("[ERROR] Quá thời gian chờ kết nối (Timeout).")
    except socket.error as e:
        print(f"[ERROR] Không thể kết nối tới Server: {e}")
    return False

#Bắt lỗi khi nhận dữ liệu (recv) bao gồm ngắt kết nối và timeout.
def safe_recv(sock: socket.socket, buffer_size: int = 1024) -> bytes | None:
    try:
        data = sock.recv(buffer_size)
        if not data:
            print("[INFO] Đối phương đã chủ động ngắt kết nối (EOF).")
            return b""
        return data
    except (ConnectionResetError, BrokenPipeError):
        print("[ERROR] Đối phương bị ngắt kết nối đột ngột!")
    except socket.timeout:
        print("[ERROR] Quá thời gian chờ nhận dữ liệu (Timeout).")
    except socket.error as e:
        print(f"[ERROR] Lỗi khi nhận dữ liệu: {e}")
    return None

#Bắt lỗi khi gửi dữ liệu (sendall) bao gồm mất kết nối.
def safe_send(sock: socket.socket, data: bytes) -> bool:
    try:
        sock.sendall(data)
        return True
    except (ConnectionResetError, BrokenPipeError):
        print("[ERROR] Không thể gửi! Mất kết nối tới đối phương.")
    except socket.timeout:
        print("[ERROR] Quá thời gian chờ gửi dữ liệu (Timeout).")
    except socket.error as e:
        print(f"[ERROR] Lỗi khi gửi dữ liệu: {e}")
    return False


def safe_close(sock: socket.socket) -> None:
    if sock:
        try:
            sock.close()
            print("[INFO] Đã đóng Socket an toàn.")
        except socket.error as e:
            print(f"[ERROR] Lỗi khi đóng Socket: {e}")
