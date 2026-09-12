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
from logger import logger
from server_gui import ask_permission

HOST = "0.0.0.0"
PORT = 5000


def handle_client(client_socket, client_address):

    client_ip = client_address[0]
    client_port = client_address[1]

    logger.info(
        f"[CONNECT] Client: {client_ip}:{client_port}"
    )
    logger.info(
        f"[THREAD] Dang xu ly Client {client_ip}:{client_port}"
    )

    try:
        while True:
            data = client_socket.recv(4096)

            if not data:
                logger.info(
                    f"[DISCONNECT] Client {client_ip}:{client_port} "
                    "da ngat ket noi."
                )
                break

            message = data.decode("utf-8")
            logger.debug(f"[RECV] {message}")

            request = parse_request(message)

            action = request.get("action", "")
            payload = request.get("payload", {})

            logger.info(f"[ACTION] {action}")

            if action == ACTION_EXECUTE:

                command = payload.get("command", "")

                logger.info(f"[COMMAND] {command}")
                logger.info("[EXECUTE] Dang thuc thi lenh...")

                result = execute_command(command)

                if result["exit_code"] == 0:

                    response = build_response(
                        STATUS_SUCCESS,
                        result["output"],
                        "Thuc thi lenh thanh cong"
                    )

                    logger.info(
                        "[EXECUTE] Thuc thi lenh thanh cong."
                    )

                else:

                    response = build_response(
                        STATUS_ERROR,
                        result["error"],
                        "Thuc thi lenh that bai"
                    )

                    logger.warning(
                        f"[EXECUTE] Thuc thi lenh that bai. "
                        f"Exit code: {result['exit_code']}"
                    )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                logger.debug(f"[SEND] {response}")

            elif action == ACTION_LIST_DIR:

                path = payload.get("path", ".")

                logger.info(f"[LIST_DIR] Path: {path}")

                result = execute_command(
                    f"dir {path}"
                )

                if result["exit_code"] == 0:

                    response = build_response(
                        STATUS_SUCCESS,
                        result["output"],
                        "Lay danh sach thu muc thanh cong"
                    )

                    logger.info(
                        "[LIST_DIR] Lay danh sach thu muc thanh cong."
                    )

                else:

                    response = build_response(
                        STATUS_ERROR,
                        result["error"],
                        "Khong the lay danh sach thu muc"
                    )

                    logger.warning(
                        "[LIST_DIR] Khong the lay danh sach thu muc."
                    )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                logger.debug(f"[SEND] {response}")

            elif action == ACTION_DISCONNECT:

                response = build_response(
                    STATUS_SUCCESS,
                    "",
                    "Server da ngat ket noi"
                )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                logger.info(
                    f"[DISCONNECT] Client {client_ip}:{client_port} "
                    "yeu cau ngat ket noi."
                )

                logger.debug(f"[SEND] {response}")

                break

            else:

                response = build_response(
                    STATUS_ERROR,
                    "",
                    "Action khong hop le"
                )

                client_socket.sendall(
                    response.encode("utf-8")
                )

                logger.warning(
                    f"[ACTION] Action khong hop le: {action}"
                )

                logger.debug(f"[SEND] {response}")

    except ConnectionResetError:

        logger.warning(
            f"[DISCONNECT] Client {client_ip}:{client_port} "
            "ngat ket noi dot ngot."
        )

    except Exception as error:

        logger.error(
            f"[ERROR] Client {client_ip}:{client_port}: {error}",
            exc_info=True
        )

    finally:

        client_socket.close()

        logger.info(
            f"[THREAD] Ket thuc xu ly Client "
            f"{client_ip}:{client_port}"
        )


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.bind(
    (HOST, PORT)
)

server_socket.listen(5)

logger.info("=" * 45)
logger.info("              TCP SERVER")
logger.info("=" * 45)
logger.info(f"[SERVER] Dang chay tai cong {PORT}")
logger.info("[SERVER] Dang cho Client ket noi...")


while True:

    client_socket, client_address = server_socket.accept()

    client_ip = client_address[0]
    client_port = client_address[1]

    logger.info("=" * 45)

    logger.info(
        f"[REQUEST] Client {client_ip}:"
        f"{client_port} yeu cau ket noi."
    )

    permission = ask_permission(
        client_ip,
        client_port
    )

    if permission == False:

        response = build_response(
            STATUS_ERROR,
            "",
            "Ket noi bi tu choi boi Server"
        )

        client_socket.sendall(
            response.encode("utf-8")
        )

        logger.warning(
            f"[PERMISSION] Client {client_ip}:"
            f"{client_port} bi tu choi."
        )

        client_socket.close()

        logger.info(
            "[SERVER] Dang cho Client tiep theo..."
        )

        continue

    logger.info(
        f"[PERMISSION] Client {client_ip}:"
        f"{client_port} da duoc cho phep."
    )

    response = build_response(
        STATUS_SUCCESS,
        "",
        "Ket noi duoc Server cho phep"
    )

    client_socket.sendall(
        response.encode("utf-8")
    )

    logger.info(
        f"[PERMISSION] Da gui xac nhan ket noi cho "
        f"Client {client_ip}:{client_port}."
    )

    client_thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address),
        daemon=True
    )

    client_thread.start()

    logger.info(
        f"[SERVER] Da tao Thread cho Client "
        f"{client_ip}:{client_port}"
    )

    logger.info(
        "[SERVER] Dang cho Client tiep theo..."
    )