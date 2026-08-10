import socket
from demo_logger import log  # Tích hợp mô-đun ghi nhật ký của Long

HOST = "0.0.0.0"
PORT = 5000

# Khởi tạo Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

log("=" * 45)
log("              TCP SERVER")
log("=" * 45)
log(f"[SERVER] Dang chay tai cong {PORT}")
log("[SERVER] Dang cho Client ket noi...")

try:
    # Lắng nghe kết nối từ Client
    client_socket, client_address = server_socket.accept()
    client_ip = client_address[0]
    client_port = client_address[1]

    log(f"[CONNECT] Client ket noi tu: {client_ip}:{client_port}")

    while True:
        try:
            # Nhận dữ liệu từ Client
            data = client_socket.recv(1024)

            if not data:
                log(f"[DISCONNECT] Client {client_ip} da ngat ket noi.")
                break

            message = data.decode("utf-8")
            log(f"[RECV] Tu {client_ip}: {message}")

            # Xử lý phản hồi
            response = "May chu da nhan duoc: " + message
            client_socket.sendall(response.encode("utf-8"))
            log(f"[SEND] Toi {client_ip}: {response}")

        except ConnectionResetError:
            log(f"[WARNING] Client {client_ip} ngat ket noi dot ngot!")
            break

    client_socket.close()

except Exception as e:
    log(f"[ERROR] Loi Server: {e}")
finally:
    server_socket.close()
    log("[SERVER] Da dong ket noi.")
    log("=" * 45)
