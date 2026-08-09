import socket

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print("=" * 45)
print("              TCP SERVER")
print("=" * 45)
print(f"[SERVER] Dang chay tai cong {PORT}")
print("[SERVER] Dang cho Client ket noi...")
print()

client_socket, client_address = server_socket.accept()

client_ip = client_address[0]
client_port = client_address[1]

print(f"[CONNECT] Client: {client_ip}:{client_port}")
print()

while True:
    data = client_socket.recv(1024)

    if not data:
        print("[DISCONNECT] Client da ngat ket noi.")
        break

    message = data.decode("utf-8")

    print(f"[RECV] {message}")

    response = "May chu da nhan duoc: " + message

    client_socket.sendall(response.encode("utf-8"))

    print(f"[SEND] {response}")
    print()

client_socket.close()
server_socket.close()

print("[SERVER] Da dong ket noi.")
print("=" * 45)