import socket

DEFAULT_TIMEOUT = 10.0


def set_timeout(sock: socket.socket, seconds: float = DEFAULT_TIMEOUT) -> None:
    """Cấu hình thời gian chờ để chống treo Server/Client."""
    if isinstance(sock, socket.socket):
        sock.settimeout(seconds)


def safe_recv_with_timeout(sock: socket.socket, bufsize: int = 1024, timeout: float = DEFAULT_TIMEOUT) -> bytes | None:
    """
    Nhận dữ liệu an toàn:
    - Đặt timeout chống treo Server nếu đối phương không gửi dữ liệu.
    - Bắt lỗi ngắt mạng đột ngột (ConnectionResetError, BrokenPipeError).
    """
    try:
        sock.settimeout(timeout)
        data = sock.recv(bufsize)
        if not data:
            print("[DISCONNECT] Đối phương đã chủ động đóng kết nối (EOF).")
            return b""
        return data

    except socket.timeout:
        print(f"[TIMEOUT] Quá thời gian {timeout}s không nhận được dữ liệu. Chống treo thành công!")
    except (ConnectionResetError, BrokenPipeError):
        print("[NET_ERROR] Phát hiện ngắt mạng đột ngột từ đối phương!")
    except socket.error as e:
        print(f"[SOCKET_ERROR] Lỗi kết nối mạng: {e}")

    return None


def safe_send_with_timeout(sock: socket.socket, data: bytes, timeout: float = DEFAULT_TIMEOUT) -> bool:
    """
    Gửi dữ liệu an toàn:
    - Đặt timeout khi gửi.
    - Bắt lỗi ngắt mạng đột ngột khi đối phương rớt mạng giữa chừng.
    """
    try:
        sock.settimeout(timeout)
        sock.sendall(data)
        return True

    except socket.timeout:
        print(f"[TIMEOUT] Gửi dữ liệu quá thời gian {timeout}s!")
    except (ConnectionResetError, BrokenPipeError):
        print("[NET_ERROR] Mất kết nối đột ngột, không thể gửi dữ liệu!")
    except socket.error as e:
        print(f"[SOCKET_ERROR] Lỗi mạng khi gửi: {e}")

    return False
