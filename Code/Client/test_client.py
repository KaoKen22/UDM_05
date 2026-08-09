import socket

HOST = "127.0.0.1"
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("=" * 45)
print("             TCP CLIENT - TEST")
print("=" * 45)

print("[CLIENT] Dang ket noi Server...")

client_socket.connect((HOST, PORT))

print("[CLIENT] Ket noi thanh cong.")
print()

while True:
    message = input("[CLIENT] Nhap du lieu: ")

    if message.lower() == "thoat":
        break

    client_socket.sendall(message.encode("utf-8"))

    print(f"[SEND] {message}")

    response = client_socket.recv(1024)

    response_message = response.decode("utf-8")

    print(f"[RECV] {response_message}")
    print()

client_socket.close()

print("[CLIENT] Da ngat ket noi.")
print("=" * 45)