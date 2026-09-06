import socket
import sys
import os
import threading

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "Shared"
        )
    )
)

from protocol import (
    ACTION_EXECUTE,
    ACTION_LIST_DIR,
    ACTION_DISCONNECT,
    STATUS_SUCCESS,
    STATUS_ERROR,
    parse_request,
    build_response
)

from command_execution import execute_command


HOST = "0.0.0.0"
PORT = 5000


def handle_client(client_socket, client_address):

    client_ip = client_address[0]
    client_port = client_address[1]

    print(f"[CONNECT] Client: {client_ip}:{client_port}")
    print(f"[THREAD] Dang xu ly Client {client_ip}:{client_port}")
    print()

    try:

        while True:

            data = client_socket.recv(4096)

            if not data:
                print(
                    f"[DISCONNECT] Client {client_ip}:{client_port} "
                    "da ngat ket noi."
                )
                break

            message = data.decode("utf-8")

            print(f"[RECV] {message}")

            # Phan tich request JSON
            request = parse_request(message)

            action = request.get("action", "")
            payload = request.get("payload", {})

            print(f"[ACTION] {action}")

            # EXECUTE

            if action == ACTION_EXECUTE:

                command = payload.get("command", "")

                print(f"[COMMAND] {command}")
                print("[EXECUTE] Dang thuc thi lenh...")

                result = execute_command(command)

                if result["exit_code"] == 0:

                    response = build_response(
                        STATUS_SUCCESS,
                        result["output"],
                        "Thuc thi lenh thanh cong"
                    )

                else:

                    response = build_response(
                        STATUS_ERROR,
                        result["error"],
                        "Thuc thi lenh that bai"
                    )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                print(f"[SEND] {response}")
                print()

            # LIST_DIR

            elif action == ACTION_LIST_DIR:

                path = payload.get("path", ".")

                print(f"[LIST_DIR] Path: {path}")

                result = execute_command(f"dir {path}")

                if result["exit_code"] == 0:

                    response = build_response(
                        STATUS_SUCCESS,
                        result["output"],
                        "Lay danh sach thu muc thanh cong"
                    )

                else:

                    response = build_response(
                        STATUS_ERROR,
                        result["error"],
                        "Khong the lay danh sach thu muc"
                    )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                print(f"[SEND] {response}")
                print()

            # DISCONNECT

            elif action == ACTION_DISCONNECT:

                response = build_response(
                    STATUS_SUCCESS,
                    "",
                    "Server da ngat ket noi"
                )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                print(
                    f"[DISCONNECT] Client {client_ip}:{client_port} "
                    "yeu cau ngat ket noi."
                )

                break

            # ACTION KHONG HOP LE

            else:

                response = build_response(
                    STATUS_ERROR,
                    "",
                    "Action khong hop le"
                )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                print(f"[SEND] {response}")
                print()

    except ConnectionResetError:

        print(
            f"[DISCONNECT] Client {client_ip}:{client_port} "
            "ngat ket noi dot ngot."
        )

    except Exception as error:

        print(
            f"[ERROR] Client {client_ip}:{client_port}: {error}"
        )

    finally:

        client_socket.close()

        print(
            f"[THREAD] Ket thuc xu ly Client "
            f"{client_ip}:{client_port}"
        )
        print()


# Tao Socket Server

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind((HOST, PORT))
server_socket.listen(5)


print("=" * 45)
print("              TCP SERVER")
print("=" * 45)
print(f"[SERVER] Dang chay tai cong {PORT}")
print("[SERVER] Dang cho Client ket noi...")
print()


# Cho nhieu Client ket noi

while True:

    client_socket, client_address = server_socket.accept()

    client_thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address),
        daemon=True
    )

    client_thread.start()

    print(
        f"[SERVER] Da tao Thread cho Client "
        f"{client_address[0]}:{client_address[1]}"
    )
    print("[SERVER] Dang cho Client tiep theo...")
    print()