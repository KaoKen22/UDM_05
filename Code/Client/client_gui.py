import tkinter as tk
from tkinter import ttk
import socket
import sys
import os
import threading
import json
import select
import time

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
    ACTION_DISCONNECT,
    build_execute_request,
    build_list_dir_request,
    build_stop_request,
    build_request,
    parse_response
)

client = None

network_lock = threading.Lock()
send_lock = threading.Lock()

command_state_lock = threading.Lock()
command_in_progress = False

# Server command timeout là 15s, nên Client chờ lâu hơn.
DEFAULT_RESPONSE_TIMEOUT = 20.0
PERMISSION_TIMEOUT = 30.0
monitor_running = False


def ui_call(func, *args, **kwargs):
    window.after(0, lambda: func(*args, **kwargs))


def append_text(text_box, message):
    text_box.insert(tk.END, message)
    text_box.see(tk.END)


def set_status(message):
    status_label.config(text=message)


def close_client_socket():
    global client, command_in_progress

    sock = client
    client = None

    with command_state_lock:
        command_in_progress = False

    if sock is not None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass

        try:
            sock.close()
        except Exception:
            pass


def start_connection_monitor():
    """Theo dõi socket nền để phát hiện Server ngắt đột ngột khi Client đang idle."""
    global monitor_running

    if monitor_running:
        return

    monitor_running = True

    threading.Thread(
        target=_connection_monitor_worker,
        daemon=True
    ).start()


def _connection_monitor_worker():
    global client, monitor_running

    try:
        while client is not None:
            sock = client

            try:
                # Chỉ kiểm tra trạng thái socket, không lấy dữ liệu khỏi socket.
                readable, _, exceptional = select.select(
                    [sock],
                    [],
                    [sock],
                    1.0
                )

                if exceptional:
                    ui_call(
                        append_text,
                        terminal,
                        "[DISCONNECT] Mất kết nối đột ngột với Server.\n"
                    )
                    ui_call(
                        set_status,
                        "Mất kết nối Server"
                    )
                    close_client_socket()
                    break

                if readable:
                    try:
                        # MSG_PEEK cho phép nhìn dữ liệu mà không lấy nó khỏi buffer.
                        peek_data = sock.recv(
                            1,
                            socket.MSG_PEEK
                        )

                        # b"" nghĩa là phía Server đã đóng connection.
                        if peek_data == b"":
                            ui_call(
                                append_text,
                                terminal,
                                "[DISCONNECT] Server đã ngắt kết nối đột ngột.\n"
                            )
                            ui_call(
                                set_status,
                                "Mất kết nối Server"
                            )
                            close_client_socket()
                            break

                    except BlockingIOError:
                        pass

                    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
                        ui_call(
                            append_text,
                            terminal,
                            "[DISCONNECT] Mất kết nối đột ngột với Server.\n"
                        )
                        ui_call(
                            set_status,
                            "Mất kết nối Server"
                        )
                        close_client_socket()
                        break

            except (ValueError, OSError):
                # Socket có thể vừa bị đóng bởi thao tác Disconnect bình thường.
                break

            time.sleep(0.2)

    finally:
        monitor_running = False


def receive_data(timeout=DEFAULT_RESPONSE_TIMEOUT):
    global client

    if client is None:
        return ""

    data = b""

    try:
        client.settimeout(timeout)

        while True:
            part = client.recv(4096)

            if not part:
                return ""

            data += part

            try:
                json.loads(data.decode("utf-8"))
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        return data.decode("utf-8", errors="ignore")

    except socket.timeout:
        return None

    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        return ""

    except OSError:
        return ""

    finally:
        if client is not None:
            try:
                client.settimeout(None)
            except Exception:
                pass


def connect_server():
    ip = ip_entry.get().strip()

    try:
        port = int(port_entry.get())
    except ValueError:
        set_status("Port không hợp lệ")
        append_text(terminal, "[ERROR] Port phải là số.\n")
        return

    if not ip:
        set_status("IP không hợp lệ")
        append_text(terminal, "[ERROR] Vui lòng nhập Server IP.\n")
        return

    threading.Thread(
        target=_connect_worker,
        args=(ip, port),
        daemon=True
    ).start()


def _connect_worker(ip, port):
    global client

    if client is not None:
        ui_call(
            append_text,
            terminal,
            "[INFO] Đang kiểm tra kết nối hiện tại...\n"
        )

        try:
            readable, _, exceptional = select.select(
                [client],
                [],
                [client],
                0
            )

            disconnected = bool(exceptional)

            if readable and not disconnected:
                try:
                    disconnected = (
                        client.recv(
                            1,
                            socket.MSG_PEEK
                        ) == b""
                    )
                except Exception:
                    disconnected = True

            if disconnected:
                close_client_socket()
            else:
                ui_call(
                    append_text,
                    terminal,
                    "[INFO] Client vẫn đang kết nối với Server.\n"
                )
                return

        except Exception:
            close_client_socket()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.settimeout(10.0)

        ui_call(set_status, "Đang kết nối Server...")
        ui_call(
            append_text,
            terminal,
            f"[CONNECT] Đang kết nối {ip}:{port}...\n"
        )

        sock.connect((ip, port))
        client = sock

        ui_call(set_status, "Đang chờ Server cho phép...")
        ui_call(
            append_text,
            terminal,
            "Đã gửi yêu cầu kết nối. Đang chờ Server cho phép...\n"
        )

        response_text = receive_data(timeout=PERMISSION_TIMEOUT)

        if response_text is None:
            ui_call(
                append_text,
                terminal,
                "[TIMEOUT] Server không phản hồi yêu cầu kết nối "
                f"trong {int(PERMISSION_TIMEOUT)} giây.\n"
            )
            ui_call(set_status, "Timeout khi chờ Server")
            close_client_socket()
            return

        if response_text == "":
            ui_call(
                append_text,
                terminal,
                "[DISCONNECT] Server đã đóng kết nối khi đang chờ cho phép.\n"
            )
            ui_call(set_status, "Server đã đóng kết nối")
            close_client_socket()
            return

        response = parse_response(response_text)

        status = response.get("status", "ERROR")
        message = response.get("message", "")

        if status == "SUCCESS":
            ui_call(set_status, "Đã được Server chấp nhận")
            ui_call(
                append_text,
                terminal,
                "[SUCCESS] Server đã chấp nhận kết nối.\n"
            )

            if message:
                ui_call(append_text, terminal, message + "\n")

            # Sau khi được Server chấp nhận, bắt đầu theo dõi kết nối nền.
            start_connection_monitor()

        else:
            ui_call(set_status, "Server từ chối kết nối")
            ui_call(
                append_text,
                terminal,
                "[ERROR] Server từ chối kết nối.\n"
            )

            if message:
                ui_call(append_text, terminal, message + "\n")

            close_client_socket()

    except socket.timeout:
        ui_call(set_status, "Kết nối timeout")
        ui_call(
            append_text,
            terminal,
            "[TIMEOUT] Không thể kết nối tới Server trong thời gian cho phép.\n"
        )
        close_client_socket()

    except ConnectionRefusedError:
        ui_call(set_status, "Kết nối thất bại")
        ui_call(
            append_text,
            terminal,
            "[ERROR] Server từ chối kết nối hoặc chưa được khởi động.\n"
        )
        close_client_socket()

    except socket.gaierror:
        ui_call(set_status, "IP/Hostname không hợp lệ")
        ui_call(
            append_text,
            terminal,
            "[ERROR] Không tìm thấy địa chỉ Server.\n"
        )
        close_client_socket()

    except Exception as error:
        ui_call(set_status, "Kết nối thất bại")
        ui_call(
            append_text,
            terminal,
            "[ERROR] Kết nối thất bại: " + str(error) + "\n"
        )
        close_client_socket()


def disconnect_server():
    if client is None:
        set_status("Chưa kết nối")
        append_text(terminal, "[INFO] Chưa kết nối Server.\n")
        return

    threading.Thread(
        target=_disconnect_worker,
        daemon=True
    ).start()


def _disconnect_worker():
    with network_lock:
        if client is None:
            return

        try:
            request = build_request(ACTION_DISCONNECT)
            client.sendall(request.encode("utf-8"))
            receive_data(timeout=3.0)
        except Exception:
            pass
        finally:
            close_client_socket()

            ui_call(set_status, "Đã ngắt kết nối")
            ui_call(
                append_text,
                terminal,
                "Đã ngắt kết nối.\n"
            )


def show_response(text_box, data):
    response = parse_response(data)

    status = response.get("status", "ERROR")
    output = response.get("output", "")
    message = response.get("message", "")
    error = response.get("error", "")
    exit_code = response.get("exit_code", None)

    text_box.insert(
        tk.END,
        "[" + str(status) + "] " + str(message) + "\n"
    )

    if output:
        text_box.insert(tk.END, str(output))

        if not str(output).endswith("\n"):
            text_box.insert(tk.END, "\n")

    if error:
        text_box.insert(
            tk.END,
            "[ERROR] " + str(error) + "\n"
        )

    if exit_code is not None:
        text_box.insert(
            tk.END,
            "[EXIT CODE] " + str(exit_code) + "\n"
        )

    text_box.see(tk.END)


def _send_request_worker(request, text_box, clear_box=False, prefix=""):
    global client

    with network_lock:
        if client is None:
            ui_call(
                append_text,
                text_box,
                "Chưa kết nối Server.\n"
            )
            return

        if clear_box:
            ui_call(text_box.delete, "1.0", tk.END)

        if prefix:
            ui_call(append_text, text_box, prefix)

        try:
            with send_lock:
                client.sendall(request.encode("utf-8"))

            result = receive_data(
                timeout=DEFAULT_RESPONSE_TIMEOUT
            )

            if result is None:
                ui_call(
                    append_text,
                    text_box,
                    "[TIMEOUT] Không nhận được phản hồi từ Server "
                    f"trong {int(DEFAULT_RESPONSE_TIMEOUT)} giây.\n"
                )
                return

            if result == "":
                ui_call(
                    append_text,
                    text_box,
                    "[DISCONNECT] Mất kết nối với Server.\n"
                )
                ui_call(
                    set_status,
                    "Mất kết nối Server"
                )

                close_client_socket()
                return

            ui_call(
                show_response,
                text_box,
                result
            )

        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            ui_call(
                append_text,
                text_box,
                "[DISCONNECT] Mất kết nối đột ngột với Server.\n"
            )
            ui_call(
                set_status,
                "Mất kết nối Server"
            )
            close_client_socket()

        except socket.timeout:
            ui_call(
                append_text,
                text_box,
                "[TIMEOUT] Thao tác mạng vượt quá thời gian cho phép.\n"
            )

        except Exception as error:
            ui_call(
                append_text,
                text_box,
                "[ERROR] " + str(error) + "\n"
            )


def _command_worker(request):
    global command_in_progress

    try:
        _send_request_worker(
            request,
            terminal
        )
    finally:
        with command_state_lock:
            command_in_progress = False


def send_command():
    global command_in_progress

    if client is None:
        append_text(
            terminal,
            "Chưa kết nối Server.\n"
        )
        return

    command = command_entry.get().strip()

    if command == "":
        return

    with command_state_lock:
        if command_in_progress:
            append_text(
                terminal,
                "[INFO] Đang có lệnh chạy. Hãy bấm STOP hoặc chờ lệnh kết thúc.\n"
            )
            return

        command_in_progress = True

    append_text(
        terminal,
        "> " + command + "\n"
    )

    command_entry.delete(0, tk.END)

    request = build_execute_request(command)

    threading.Thread(
        target=_command_worker,
        args=(request,),
        daemon=True
    ).start()


def stop_command():
    if client is None:
        append_text(
            terminal,
            "[INFO] Chưa kết nối Server.\n"
        )
        return

    with command_state_lock:
        running = command_in_progress

    if not running:
        append_text(
            terminal,
            "[INFO] Không có lệnh nào đang chạy để STOP.\n"
        )
        return

    threading.Thread(
        target=_stop_command_worker,
        daemon=True
    ).start()


def _stop_command_worker():
    global client

    try:
        request = build_stop_request()

        # Không dùng network_lock:
        # EXECUTE đang giữ lock này trong lúc chờ response.
        with send_lock:
            if client is None:
                return

            client.sendall(
                request.encode("utf-8")
            )

        ui_call(
            append_text,
            terminal,
            "[STOP] Đã gửi yêu cầu dừng lệnh tới Server.\n"
        )

        # Không recv() ở đây. Worker EXECUTE sẽ nhận response cuối cùng.

    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError):
        ui_call(
            append_text,
            terminal,
            "[DISCONNECT] Không thể gửi STOP vì đã mất kết nối Server.\n"
        )
        ui_call(
            set_status,
            "Mất kết nối Server"
        )
        close_client_socket()


def view_files():
    if client is None:
        append_text(
            file_text,
            "Chưa kết nối Server.\n"
        )
        return

    path = path_entry.get().strip()

    if path == "":
        path = "."

    request = build_list_dir_request(path)

    threading.Thread(
        target=_send_request_worker,
        args=(request, file_text, True),
        daemon=True
    ).start()


def refresh_tasks():
    if client is None:
        append_text(
            task_text,
            "Chưa kết nối Server.\n"
        )
        return

    request = build_execute_request("tasklist")

    threading.Thread(
        target=_send_request_worker,
        args=(request, task_text, True),
        daemon=True
    ).start()


def end_task():
    if client is None:
        append_text(
            task_text,
            "Chưa kết nối Server.\n"
        )
        return

    pid = pid_entry.get().strip()

    if pid == "":
        append_text(
            task_text,
            "Vui lòng nhập PID.\n"
        )
        return

    if not pid.isdigit():
        append_text(
            task_text,
            "PID phải là số.\n"
        )
        return

    command = "taskkill /PID " + pid + " /F"
    request = build_execute_request(command)

    pid_entry.delete(0, tk.END)

    threading.Thread(
        target=_send_request_worker,
        args=(
            request,
            task_text,
            False,
            "\n> " + command + "\n"
        ),
        daemon=True
    ).start()


window = tk.Tk()
window.title("TCP Client")
window.geometry("700x700")

tk.Label(
    window,
    text="TCP CLIENT",
    font=("Arial", 18)
).pack(pady=15)

tk.Label(
    window,
    text="Server IP"
).pack()

ip_entry = tk.Entry(window)
ip_entry.insert(0, "127.0.0.1")
ip_entry.pack()

tk.Label(
    window,
    text="Port"
).pack()

port_entry = tk.Entry(window)
port_entry.insert(0, "5000")
port_entry.pack()

tk.Button(
    window,
    text="CONNECT",
    command=connect_server
).pack(pady=8)

tk.Button(
    window,
    text="DISCONNECT",
    command=disconnect_server
).pack()

status_label = tk.Label(
    window,
    text="Chưa kết nối"
)
status_label.pack(pady=10)

tabs = ttk.Notebook(window)
tabs.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

terminal_tab = tk.Frame(tabs)
tabs.add(terminal_tab, text="Terminal")

terminal = tk.Text(
    terminal_tab,
    bg="black",
    fg="white"
)
terminal.pack(
    fill="both",
    expand=True,
    padx=5,
    pady=5
)

command_frame = tk.Frame(terminal_tab)
command_frame.pack(
    fill="x",
    padx=5,
    pady=5
)

tk.Label(
    command_frame,
    text="Command:"
).pack(side="left")

command_entry = tk.Entry(command_frame)
command_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)

tk.Button(
    command_frame,
    text="STOP",
    command=stop_command
).pack(
    side="right",
    padx=(0, 5)
)

tk.Button(
    command_frame,
    text="SEND",
    command=send_command
).pack(side="right")

command_entry.bind(
    "<Return>",
    lambda event: send_command()
)

file_tab = tk.Frame(tabs)
tabs.add(file_tab, text="File Browser")

tk.Label(
    file_tab,
    text="Đường dẫn:"
).pack(pady=5)

path_frame = tk.Frame(file_tab)
path_frame.pack(
    fill="x",
    padx=10
)

path_entry = tk.Entry(path_frame)
path_entry.insert(0, ".")
path_entry.pack(
    side="left",
    fill="x",
    expand=True
)

tk.Button(
    path_frame,
    text="XEM FILE",
    command=view_files
).pack(
    side="right",
    padx=5
)

file_text = tk.Text(file_tab)
file_text.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

task_tab = tk.Frame(tabs)
tabs.add(task_tab, text="Task Manager")

tk.Button(
    task_tab,
    text="REFRESH",
    command=refresh_tasks
).pack(pady=8)

pid_frame = tk.Frame(task_tab)
pid_frame.pack(
    fill="x",
    padx=10,
    pady=5
)

tk.Label(
    pid_frame,
    text="PID:"
).pack(side="left")

pid_entry = tk.Entry(pid_frame)
pid_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)

tk.Button(
    pid_frame,
    text="END TASK",
    command=end_task
).pack(side="right")

task_text = tk.Text(task_tab)
task_text.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)


def close_window():
    close_client_socket()
    window.destroy()


window.protocol(
    "WM_DELETE_WINDOW",
    close_window
)

window.mainloop()
