import tkinter as tk
from tkinter import ttk
import socket
import os
import importlib.util
import threading


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

PROTOCOL_PATH = os.path.join(
    BASE_DIR,
    "Shared",
    "protocol.py"
)

if not os.path.isfile(PROTOCOL_PATH):
    raise FileNotFoundError(
        "Khong tim thay Shared/protocol.py:\n"
        + PROTOCOL_PATH
    )

spec = importlib.util.spec_from_file_location(
    "protocol",
    PROTOCOL_PATH
)

if spec is None or spec.loader is None:
    raise ImportError(
        "Khong the nap Shared/protocol.py"
    )

protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protocol)

ACTION_DISCONNECT = protocol.ACTION_DISCONNECT
build_execute_request = protocol.build_execute_request
build_list_dir_request = protocol.build_list_dir_request
build_request = protocol.build_request
parse_response = protocol.parse_response


client = None
connected = False
waiting_permission = False


def show_response(text_box, data):
    response = parse_response(data)

    status = response.get(
        "status",
        "ERROR"
    )

    output = response.get(
        "output",
        ""
    )

    message = response.get(
        "message",
        ""
    )

    text_box.insert(
        tk.END,
        "[" + status + "] "
        + message
        + "\n"
    )

    if output:
        text_box.insert(
            tk.END,
            output
        )

        if not output.endswith("\n"):
            text_box.insert(
                tk.END,
                "\n"
            )

def receive_data():
    if client is None:
        return ""

    data = b""

    try:
        client.settimeout(0.5)

        while True:
            part = client.recv(4096)

            if not part:
                break

            data += part

    except socket.timeout:
        pass

    except Exception:
        pass

    finally:
        try:
            client.settimeout(None)
        except Exception:
            pass

    return data.decode(
        "utf-8",
        errors="ignore"
    )


def wait_server_permission():
    if client is None:
        return ""

    try:
 
        client.settimeout(120)

        data = client.recv(65535)

        if not data:
            return ""

        return data.decode(
            "utf-8",
            errors="ignore"
        )

    except socket.timeout:
        return ""

    except Exception:
        return ""

    finally:
        try:
            client.settimeout(None)
        except Exception:
            pass


def permission_worker():
    result = wait_server_permission()

    window.after(
        0,
        finish_connect,
        result
    )


def finish_connect(result):
    global client
    global connected
    global waiting_permission

    waiting_permission = False

    if result == "":
        connected = False

        if client is not None:
            try:
                client.close()
            except Exception:
                pass

        client = None

        status_label.config(
            text="Khong nhan duoc phan hoi"
        )

        terminal.insert(
            tk.END,
            "[ERROR] Khong nhan duoc goi phan hoi tu Server.\n"
        )

        set_controls(False)
        return

    response = parse_response(result)

    status = response.get(
        "status",
        "ERROR"
    )

    message = response.get(
        "message",
        ""
    )

    if status == "SUCCESS":
        connected = True

        status_label.config(
            text="Da ket noi Server"
        )

        terminal.insert(
            tk.END,
            "Server da cho phep ket noi.\n"
        )

        terminal.insert(
            tk.END,
            "Da ket noi Server.\n"
        )

        set_controls(True)

    else:
        connected = False

        if client is not None:
            try:
                client.close()
            except Exception:
                pass

        client = None

        status_label.config(
            text="Ket noi bi tu choi"
        )

        terminal.insert(
            tk.END,
            "[ERROR] "
            + (
                message
                if message
                else "Server tu choi ket noi."
            )
            + "\n"
        )

        set_controls(False)

    terminal.see(tk.END)

def connect_server():
    global client
    global connected
    global waiting_permission

    if connected or waiting_permission:
        return

    ip = ip_entry.get().strip()

    try:
        port = int(
            port_entry.get().strip()
        )

    except ValueError:
        status_label.config(
            text="Port khong hop le"
        )

        terminal.insert(
            tk.END,
            "[ERROR] Port phai la so.\n"
        )

        return

    try:
        client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client.settimeout(10)

        client.connect(
            (ip, port)
        )

        client.settimeout(None)

        connected = False
        waiting_permission = True

        status_label.config(
            text="Dang cho Server cho phep..."
        )

        terminal.insert(
            tk.END,
            "Da ket noi TCP.\n"
        )

        terminal.insert(
            tk.END,
            "Dang cho Server cho phep...\n"
        )

        terminal.see(tk.END)

        set_controls(False)


        thread = threading.Thread(
            target=permission_worker,
            daemon=True
        )

        thread.start()

    except Exception as error:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass

        client = None
        connected = False
        waiting_permission = False

        status_label.config(
            text="Ket noi that bai"
        )

        terminal.insert(
            tk.END,
            "Ket noi that bai: "
            + str(error)
            + "\n"
        )

        set_controls(False)

def disconnect_server():
    global client
    global connected
    global waiting_permission

    if client is None:
        connected = False
        waiting_permission = False

        status_label.config(
            text="Chua ket noi"
        )

        set_controls(False)
        return

    try:
        if connected:
            request = build_request(
                ACTION_DISCONNECT
            )

            client.sendall(
                request.encode("utf-8")
            )

            receive_data()

    except Exception:
        pass

    try:
        client.close()
    except Exception:
        pass

    client = None
    connected = False
    waiting_permission = False

    status_label.config(
        text="Da ngat ket noi"
    )

    terminal.insert(
        tk.END,
        "Da ngat ket noi.\n"
    )

    terminal.see(tk.END)

    set_controls(False)

def send_command():
    if client is None or not connected:
        terminal.insert(
            tk.END,
            "Chua duoc Server cho phep ket noi.\n"
        )

        return

    command = command_entry.get().strip()

    if command == "":
        return

    try:
        terminal.insert(
            tk.END,
            "> " + command + "\n"
        )

        request = build_execute_request(
            command
        )

        client.sendall(
            request.encode("utf-8")
        )

        result = receive_data()

        if result == "":
            terminal.insert(
                tk.END,
                "[ERROR] Khong nhan duoc phan hoi.\n"
            )

            return

        show_response(
            terminal,
            result
        )

        terminal.insert(
            tk.END,
            "\n"
        )

        terminal.see(tk.END)

        command_entry.delete(
            0,
            tk.END
        )

    except Exception as error:
        terminal.insert(
            tk.END,
            "[ERROR] "
            + str(error)
            + "\n"
        )

def view_files():
    if client is None or not connected:
        file_text.insert(
            tk.END,
            "Chua duoc Server cho phep ket noi.\n"
        )

        return

    path = path_entry.get().strip()

    if path == "":
        path = "."

    try:
        request = build_list_dir_request(
            path
        )

        client.sendall(
            request.encode("utf-8")
        )

        result = receive_data()

        file_text.delete(
            "1.0",
            tk.END
        )

        if result == "":
            file_text.insert(
                tk.END,
                "[ERROR] Khong nhan duoc phan hoi.\n"
            )

            return

        show_response(
            file_text,
            result
        )

        file_text.see(
            tk.END
        )

    except Exception as error:
        file_text.delete(
            "1.0",
            tk.END
        )

        file_text.insert(
            tk.END,
            "[ERROR] "
            + str(error)
        )

def refresh_tasks():
    if client is None or not connected:
        task_text.insert(
            tk.END,
            "Chua duoc Server cho phep ket noi.\n"
        )

        return

    try:
        request = build_execute_request(
            "tasklist"
        )

        client.sendall(
            request.encode("utf-8")
        )

        result = receive_data()

        task_text.delete(
            "1.0",
            tk.END
        )

        if result == "":
            task_text.insert(
                tk.END,
                "[ERROR] Khong nhan duoc phan hoi.\n"
            )

            return

        show_response(
            task_text,
            result
        )

        task_text.see(
            tk.END
        )

    except Exception as error:
        task_text.delete(
            "1.0",
            tk.END
        )

        task_text.insert(
            tk.END,
            "[ERROR] "
            + str(error)
        )


def end_task():
    if client is None or not connected:
        task_text.insert(
            tk.END,
            "Chua duoc Server cho phep ket noi.\n"
        )

        return

    pid = pid_entry.get().strip()

    if pid == "":
        task_text.insert(
            tk.END,
            "Vui long nhap PID.\n"
        )

        return

    if not pid.isdigit():
        task_text.insert(
            tk.END,
            "PID phai la so.\n"
        )

        return

    try:
        command = (
            "taskkill /PID "
            + pid
            + " /F"
        )

        request = build_execute_request(
            command
        )

        client.sendall(
            request.encode("utf-8")
        )

        result = receive_data()

        task_text.insert(
            tk.END,
            "\n> " + command + "\n"
        )

        if result == "":
            task_text.insert(
                tk.END,
                "[ERROR] Khong nhan duoc phan hoi.\n"
            )

            return

        show_response(
            task_text,
            result
        )

        task_text.see(
            tk.END
        )

        pid_entry.delete(
            0,
            tk.END
        )

    except Exception as error:
        task_text.insert(
            tk.END,
            "[ERROR] "
            + str(error)
            + "\n"
        )

def set_controls(enabled):
    state = "normal" if enabled else "disabled"

    command_entry.config(
        state=state
    )

    send_button.config(
        state=state
    )

    path_entry.config(
        state=state
    )

    file_button.config(
        state=state
    )

    refresh_button.config(
        state=state
    )

    pid_entry.config(
        state=state
    )

    end_task_button.config(
        state=state
    )
window = tk.Tk()

window.title(
    "TCP Client"
)

window.geometry(
    "700x700"
)


tk.Label(
    window,
    text="TCP CLIENT",
    font=("Arial", 18)
).pack(
    pady=15
)


tk.Label(
    window,
    text="Server IP"
).pack()


ip_entry = tk.Entry(
    window
)

ip_entry.insert(
    0,
    "127.0.0.1"
)

ip_entry.pack()


tk.Label(
    window,
    text="Port"
).pack()


port_entry = tk.Entry(
    window
)

port_entry.insert(
    0,
    "5000"
)

port_entry.pack()


tk.Button(
    window,
    text="CONNECT",
    command=connect_server
).pack(
    pady=8
)


tk.Button(
    window,
    text="DISCONNECT",
    command=disconnect_server
).pack()


status_label = tk.Label(
    window,
    text="Chua ket noi"
)

status_label.pack(
    pady=10
)


tabs = ttk.Notebook(
    window
)

tabs.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

terminal_tab = tk.Frame(
    tabs
)

tabs.add(
    terminal_tab,
    text="Terminal"
)


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


command_frame = tk.Frame(
    terminal_tab
)

command_frame.pack(
    fill="x",
    padx=5,
    pady=5
)


tk.Label(
    command_frame,
    text="Command:"
).pack(
    side="left"
)


command_entry = tk.Entry(
    command_frame
)

command_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)


send_button = tk.Button(
    command_frame,
    text="SEND",
    command=send_command
)

send_button.pack(
    side="right"
)


command_entry.bind(
    "<Return>",
    lambda event: send_command()
)

file_tab = tk.Frame(
    tabs
)

tabs.add(
    file_tab,
    text="File Browser"
)


tk.Label(
    file_tab,
    text="Duong dan:"
).pack(
    pady=5
)


path_frame = tk.Frame(
    file_tab
)

path_frame.pack(
    fill="x",
    padx=10
)


path_entry = tk.Entry(
    path_frame
)

path_entry.insert(
    0,
    "."
)

path_entry.pack(
    side="left",
    fill="x",
    expand=True
)


file_button = tk.Button(
    path_frame,
    text="XEM FILE",
    command=view_files
)

file_button.pack(
    side="right",
    padx=5
)


file_text = tk.Text(
    file_tab
)

file_text.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

task_tab = tk.Frame(
    tabs
)

tabs.add(
    task_tab,
    text="Task Manager"
)


refresh_button = tk.Button(
    task_tab,
    text="REFRESH",
    command=refresh_tasks
)

refresh_button.pack(
    pady=8
)


pid_frame = tk.Frame(
    task_tab
)

pid_frame.pack(
    fill="x",
    padx=10,
    pady=5
)


tk.Label(
    pid_frame,
    text="PID:"
).pack(
    side="left"
)


pid_entry = tk.Entry(
    pid_frame
)

pid_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)


end_task_button = tk.Button(
    pid_frame,
    text="END TASK",
    command=end_task
)

end_task_button.pack(
    side="right"
)


task_text = tk.Text(
    task_tab
)

task_text.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)

set_controls(False)

def close_window():
    if client is not None:
        disconnect_server()

    window.destroy()


window.protocol(
    "WM_DELETE_WINDOW",
    close_window
)


window.mainloop()
