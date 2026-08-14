import socket
import json

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

while True:
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

        try:
            request = json.loads(message)

            action = request.get("action", "")
            command = request.get("command", "")

            print(f"[ACTION] {action}")
            print(f"[COMMAND] {command}")

            if action == "DISCONNECT":
                print("[DISCONNECT] Client yeu cau ngat ket noi.")
                break

            if action == "EXECUTE":
                print("[EXECUTE] Server nhan yeu cau thuc thi lenh.")

                response = json.dumps({
                    "status": "SUCCESS",
                    "output": "",
                    "message": "Server da nhan yeu cau thuc thi"
                })

                client_socket.sendall(response.encode("utf-8"))

                print(f"[SEND] {response}")
                print()

                continue

            response = json.dumps({
                "status": "ERROR",
                "output": "",
                "message": "Action khong hop le"
            })

            client_socket.sendall(response.encode("utf-8"))

            print(f"[SEND] {response}")
            print()

        except json.JSONDecodeError:
            print("[ERROR] Du lieu JSON khong hop le.")

            response = json.dumps({
                "status": "ERROR",
                "output": "",
                "message": "Du lieu JSON khong hop le"
            })

            client_socket.sendall(response.encode("utf-8"))

            print(f"[SEND] {response}")
            print()

    client_socket.close()

    print("[SERVER] Dang cho Client tiep theo...")
    print()