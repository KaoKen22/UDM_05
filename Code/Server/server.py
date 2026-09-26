import socket
import sys
import os
import threading

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "Shared"
        )
    )
)

from protocol import (
    ACTION_EXECUTE,
    ACTION_LIST_DIR,
    ACTION_STOP,
    ACTION_DISCONNECT,
    STATUS_SUCCESS,
    STATUS_ERROR,
    parse_request,
    build_response
)

from command_execution import (
    execute_command,
    stop_process
)

from logger import logger
from server_gui import ask_permission
from time_out import safe_send_with_timeout


HOST = "0.0.0.0"
PORT = 5000

COMMAND_TIMEOUT = 15


def send_response(client_socket, send_lock, response):
    with send_lock:
        return safe_send_with_timeout(
            client_socket,
            response.encode("utf-8")
        )


def handle_client(client_socket, client_address):
    client_ip, client_port = client_address

    logger.info(
        f"[CONNECT] Client {client_ip}:{client_port} connected."
    )

    send_lock = threading.Lock()
    state_lock = threading.Lock()

    state = {
        "running": False,
        "process": None,
        "stop_event": None,
        "command": None
    }

    receive_buffer = ""

    def set_process(process):
        with state_lock:
            state["process"] = process
            stop_event = state["stop_event"]

        # STOP có thể tới ngay lúc process vừa được tạo.
        if stop_event is not None and stop_event.is_set():
            stop_process(process)

    def execute_worker(command):
        try:
            result = execute_command(
                command,
                timeout=COMMAND_TIMEOUT,
                process_callback=set_process,
                stop_event=state["stop_event"]
            )

            if result.get("stopped"):
                logger.info(
                    f"[STOP] Client {client_ip}:{client_port} "
                    f"stopped command: {command}"
                )

                response = build_response(
                    STATUS_SUCCESS,
                    output=result.get("output", ""),
                    message="Lệnh đã được người dùng dừng.",
                    error="",
                    exit_code=result.get("exit_code", -2)
                )

            elif result.get("timed_out"):
                logger.warning(
                    f"[COMMAND_TIMEOUT] Client {client_ip}:{client_port} "
                    f"command: {command}"
                )

                response = build_response(
                    STATUS_ERROR,
                    output=result.get("output", ""),
                    message="Lệnh chạy quá thời gian cho phép.",
                    error=result.get("error", ""),
                    exit_code=result.get("exit_code", -1)
                )

            elif result.get("exit_code") == 0:
                logger.info(
                    f"[COMMAND_SUCCESS] Client {client_ip}:{client_port} "
                    f"command: {command}, exit_code=0"
                )

                response = build_response(
                    STATUS_SUCCESS,
                    output=result.get("output", ""),
                    message="Thực thi lệnh thành công.",
                    error=result.get("error", ""),
                    exit_code=result.get("exit_code", 0)
                )

            else:
                logger.warning(
                    f"[COMMAND_ERROR] Client {client_ip}:{client_port} "
                    f"command: {command}, "
                    f"exit_code={result.get('exit_code')}"
                )

                response = build_response(
                    STATUS_ERROR,
                    output=result.get("output", ""),
                    message="Thực thi lệnh thất bại.",
                    error=result.get("error", ""),
                    exit_code=result.get("exit_code", -1)
                )

            send_response(
                client_socket,
                send_lock,
                response
            )

        except Exception as error:
            logger.exception(
                f"[ERROR] Execute worker failed for "
                f"{client_ip}:{client_port}: {error}"
            )

            response = build_response(
                STATUS_ERROR,
                message="Lỗi khi thực thi lệnh.",
                error=str(error),
                exit_code=-1
            )

            send_response(
                client_socket,
                send_lock,
                response
            )

        finally:
            with state_lock:
                state["running"] = False
                state["process"] = None
                state["stop_event"] = None
                state["command"] = None

    def process_request(message):
        request = parse_request(message)

        action = request.get("action", "")
        payload = request.get("payload", {})

        if action == ACTION_EXECUTE:
            command = payload.get("command", "")

            with state_lock:
                if state["running"]:
                    response = build_response(
                        STATUS_ERROR,
                        message="Đang có một lệnh khác chạy.",
                        error="Hãy STOP hoặc chờ lệnh hiện tại kết thúc."
                    )

                    send_response(
                        client_socket,
                        send_lock,
                        response
                    )
                    return True

                state["running"] = True
                state["process"] = None
                state["stop_event"] = threading.Event()
                state["command"] = command

            logger.info(
                f"[EXECUTE] Client {client_ip}:{client_port} "
                f"command: {command}"
            )

            threading.Thread(
                target=execute_worker,
                args=(command,),
                daemon=True
            ).start()

            # Không chờ command ở đây để Server vẫn nhận được ACTION_STOP.
            return True

        if action == ACTION_STOP:
            with state_lock:
                running = state["running"]
                process = state["process"]
                stop_event = state["stop_event"]
                command = state["command"]

                if running and stop_event is not None:
                    stop_event.set()

            if not running:
                logger.info(
                    f"[STOP] Client {client_ip}:{client_port} "
                    f"requested STOP but no command was running."
                )
                return True

            logger.info(
                f"[STOP_REQUEST] Client {client_ip}:{client_port} "
                f"requested stop for command: {command}"
            )

            if process is not None:
                stop_process(process)

            # Không gửi response thứ hai ở đây.
            # execute_worker sẽ trả kết quả cuối cùng "đã dừng".
            return True

        if action == ACTION_LIST_DIR:
            path = payload.get("path", ".")

            with state_lock:
                if state["running"]:
                    response = build_response(
                        STATUS_ERROR,
                        message="Đang có một lệnh khác chạy.",
                        error="Hãy STOP hoặc chờ lệnh hiện tại kết thúc."
                    )

                    send_response(
                        client_socket,
                        send_lock,
                        response
                    )
                    return True

                state["running"] = True
                state["process"] = None
                state["stop_event"] = threading.Event()
                state["command"] = f'dir "{path}"'

            threading.Thread(
                target=execute_worker,
                args=(f'dir "{path}"',),
                daemon=True
            ).start()

            return True

        if action == ACTION_DISCONNECT:
            with state_lock:
                process = state["process"]
                stop_event = state["stop_event"]

                if stop_event is not None:
                    stop_event.set()

            if process is not None:
                stop_process(process)

            response = build_response(
                STATUS_SUCCESS,
                message="Đã ngắt kết nối."
            )

            send_response(
                client_socket,
                send_lock,
                response
            )

            return False

        parse_error = request.get(
            "parse_error",
            "Action không hợp lệ."
        )

        response = build_response(
            STATUS_ERROR,
            message="Request không hợp lệ.",
            error=parse_error
        )

        send_response(
            client_socket,
            send_lock,
            response
        )

        return True

    try:
        # Timeout ngắn để recv không chờ vô hạn, nhưng idle Client không bị kick.
        client_socket.settimeout(1.0)

        while True:
            try:
                data = client_socket.recv(4096)

            except socket.timeout:
                continue

            if not data:
                logger.info(
                    f"[DISCONNECT] Client {client_ip}:{client_port} "
                    f"đã đóng kết nối."
                )
                break

            receive_buffer += data.decode(
                "utf-8",
                errors="replace"
            )

            # Xử lý từng JSON message hoàn chỉnh.
            while "\n" in receive_buffer:
                message, receive_buffer = receive_buffer.split(
                    "\n",
                    1
                )

                message = message.strip()

                if not message:
                    continue

                keep_connection = process_request(
                    message
                )

                if not keep_connection:
                    return

    except ConnectionResetError:
        logger.warning(
            f"[DISCONNECT] Client {client_ip}:{client_port} "
            f"ngắt kết nối đột ngột."
        )

    except Exception as error:
        logger.exception(
            f"[ERROR] Client {client_ip}:{client_port}: {error}"
        )

    finally:
        with state_lock:
            process = state["process"]
            stop_event = state["stop_event"]

            if stop_event is not None:
                stop_event.set()

        if process is not None:
            stop_process(process)

        try:
            client_socket.close()
        except Exception:
            pass

        logger.info(
            f"[CLOSE] Closed Client {client_ip}:{client_port}."
        )


def start_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen(5)

    logger.info(
        f"[SERVER] Listening on {HOST}:{PORT}"
    )

    try:
        while True:
            client_socket, client_address = (
                server_socket.accept()
            )

            client_ip, client_port = client_address

            logger.info(
                f"[PERMISSION] Connection request from "
                f"{client_ip}:{client_port}"
            )

            allowed = ask_permission(
                client_ip,
                client_port
            )

            if not allowed:
                response = build_response(
                    STATUS_ERROR,
                    message="Kết nối bị người dùng Server từ chối."
                )

                safe_send_with_timeout(
                    client_socket,
                    response.encode("utf-8")
                )

                client_socket.close()

                logger.info(
                    f"[REJECT] Client {client_ip}:{client_port}"
                )

                continue

            response = build_response(
                STATUS_SUCCESS,
                message="Kết nối được Server cho phép."
            )

            if not safe_send_with_timeout(
                client_socket,
                response.encode("utf-8")
            ):
                client_socket.close()
                continue

            logger.info(
                f"[ACCEPT] Client {client_ip}:{client_port}"
            )

            threading.Thread(
                target=handle_client,
                args=(
                    client_socket,
                    client_address
                ),
                daemon=True
            ).start()

    except KeyboardInterrupt:
        logger.info("[SERVER] Server stopped by user.")

    finally:
        try:
            server_socket.close()
        except Exception:
            pass


if __name__ == "__main__":
    start_server()
