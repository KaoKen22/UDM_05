import tkinter as tk
from tkinter import ttk
import socket
import sys
import os

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
    build_execute_request,
    build_list_dir_request,
    build_request,
    parse_response,
    ACTION_DISCONNECT
)

client = None

def receive_data():

    global client

    if client is None:
        return ""

    try:
        data = client.recv(65536)

        if not data:
            return ""

        return data.decode("utf-8")

    except socket.timeout:
        return ""

    except Exception:
        return ""
def connect_server():

    global client

    if client is not None:
        status_label.config(
            text="Đã kết nối"
        )
        return

    ip = ip_entry.get().strip()

    try:
        port = int(port_entry.get())

    except ValueError:
        status_label.config(
            text="Port không hợp lệ"
        )
        return

    try:
        client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client.settimeout(5)

        client.connect(
            (ip, port)
        )

        client.settimeout(None)

        status_label.config(
            text="Đã kết nối Server"
        )

        terminal_output.insert(
            tk.END,
            "[SYSTEM] Đã kết nối Server\n"
        )

        terminal_output.see(
            tk.END
        )

    except Exception as error:

        if client is not None:
            client.close()

        client = None

        status_label.config(
            text="Kết nối thất bại"
        )

        terminal_output.insert(
            tk.END,
            f"[ERROR] {error}\n"
        )

def disconnect_server():

    global client

    if client is None:

        status_label.config(
            text="Chưa kết nối"
        )

        return

    try:

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

    status_label.config(
        text="Đã ngắt kết nối"
    )

    terminal_output.insert(
        tk.END,
        "[SYSTEM] Đã ngắt kết nối Server\n"
    )

    terminal_output.see(
        tk.END
    )

def show_response(output_box, response):

    status = response.get(
        "status",
        ""
    )

    output = response.get(
        "output",
        ""
    )

    message = response.get(
        "message",
        ""
    )

    output_box.insert(
        tk.END,
        f"[{status}] {message}\n"
    )

    if output:
        output_box.insert(
            tk.END,
            output
        )

        if not output.endswith("\n"):
            output_box.insert(
                tk.END,
                "\n"
            )

def send_command():

    if client is None:

        terminal_output.insert(
            tk.END,
            "[ERROR] Chưa kết nối Server\n"
        )

        return

    command = command_entry.get().strip()

    if command == "":
        return

    try:

        request = build_execute_request(
            command
        )

        client.sendall(
            request.encode("utf-8")
        )

        data = receive_data()

        if data == "":

            terminal_output.insert(
                tk.END,
                "[ERROR] Không nhận được dữ liệu từ Server\n"
            )

            return

        response = parse_response(
            data
        )

        terminal_output.insert(
            tk.END,
            f"> {command}\n"
        )

        show_response(
            terminal_output,
            response
        )

        terminal_output.insert(
            tk.END,
            "\n"
        )

        terminal_output.see(
            tk.END
        )

        command_entry.delete(
            0,
            tk.END
        )

    except Exception as error:

        terminal_output.insert(
            tk.END,
            f"[ERROR] {error}\n"
        )

def view_files():

    if client is None:

        file_output.delete(
            "1.0",
            tk.END
        )

        file_output.insert(
            tk.END,
            "[ERROR] Chưa kết nối Server"
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

        data = receive_data()

        if data == "":

            file_output.delete(
                "1.0",
                tk.END
            )

            file_output.insert(
                tk.END,
                "[ERROR] Không nhận được dữ liệu từ Server"
            )

            return

        response = parse_response(
            data
        )

        file_output.delete(
            "1.0",
            tk.END
        )

        show_response(
            file_output,
            response
        )

        file_output.see(
            tk.END
        )

    except Exception as error:

        file_output.delete(
            "1.0",
            tk.END
        )

        file_output.insert(
            tk.END,
            f"[ERROR] {error}"
        )

def refresh_tasks():

    if client is None:

        task_output.delete(
            "1.0",
            tk.END
        )

        task_output.insert(
            tk.END,
            "[ERROR] Chưa kết nối Server"
        )

        return

    try:

        request = build_execute_request(
            "tasklist"
        )

        client.sendall(
            request.encode("utf-8")
        )

        data = receive_data()

        if data == "":

            task_output.delete(
                "1.0",
                tk.END
            )

            task_output.insert(
                tk.END,
                "[ERROR] Không nhận được dữ liệu từ Server"
            )

            return

        response = parse_response(
            data
        )

        task_output.delete(
            "1.0",
            tk.END
        )

        show_response(
            task_output,
            response
        )

        task_output.see(
            tk.END
        )

    except Exception as error:

        task_output.delete(
            "1.0",
            tk.END
        )

        task_output.insert(
            tk.END,
            f"[ERROR] {error}"
        )

def end_task():

    if client is None:

        task_output.insert(
            tk.END,
            "\n[ERROR] Chưa kết nối Server\n"
        )

        return

    pid = pid_entry.get().strip()

    if pid == "":

        task_output.insert(
            tk.END,
            "\n[ERROR] Vui lòng nhập PID\n"
        )

        return

    if not pid.isdigit():

        task_output.insert(
            tk.END,
            "\n[ERROR] PID phải là số\n"
        )

        return

    command = f"taskkill /PID {pid} /F"

    try:

        request = build_execute_request(
            command
        )

        client.sendall(
            request.encode("utf-8")
        )

        data = receive_data()

        if data == "":

            task_output.insert(
                tk.END,
                "\n[ERROR] Không nhận được dữ liệu từ Server\n"
            )

            return

        response = parse_response(
            data
        )

        task_output.insert(
            tk.END,
            f"\n> {command}\n"
        )

        show_response(
            task_output,
            response
        )

        task_output.insert(
            tk.END,
            "\n"
        )

        task_output.see(
            tk.END
        )

    except Exception as error:

        task_output.insert(
            tk.END,
            f"\n[ERROR] {error}\n"
        )


window = tk.Tk()

window.title(
    "TCP Client"
)

window.geometry(
    "900x650"
)

window.minsize(
    700,
    500
)

connection_frame = tk.Frame(
    window
)

connection_frame.pack(
    fill="x",
    padx=10,
    pady=10
)


tk.Label(
    connection_frame,
    text="Server IP:"
).pack(
    side="left"
)


ip_entry = tk.Entry(
    connection_frame,
    width=15
)

ip_entry.insert(
    0,
    "127.0.0.1"
)

ip_entry.pack(
    side="left",
    padx=5
)


tk.Label(
    connection_frame,
    text="Port:"
).pack(
    side="left"
)


port_entry = tk.Entry(
    connection_frame,
    width=8
)

port_entry.insert(
    0,
    "5000"
)

port_entry.pack(
    side="left",
    padx=5
)


tk.Button(
    connection_frame,
    text="CONNECT",
    command=connect_server
).pack(
    side="left",
    padx=5
)


tk.Button(
    connection_frame,
    text="DISCONNECT",
    command=disconnect_server
).pack(
    side="left"
)


status_label = tk.Label(
    connection_frame,
    text="Chưa kết nối"
)

status_label.pack(
    side="left",
    padx=10
)
notebook = ttk.Notebook(
    window
)

notebook.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)

terminal_tab = tk.Frame(
    notebook
)

notebook.add(
    terminal_tab,
    text="Terminal"
)


terminal_output = tk.Text(
    terminal_tab,
    bg="black",
    fg="white",
    insertbackground="white"
)

terminal_output.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


command_frame = tk.Frame(
    terminal_tab
)

command_frame.pack(
    fill="x",
    padx=10,
    pady=10
)


command_entry = tk.Entry(
    command_frame
)

command_entry.pack(
    side="left",
    fill="x",
    expand=True
)


tk.Button(
    command_frame,
    text="SEND",
    width=10,
    command=send_command
).pack(
    side="left",
    padx=5
)


command_entry.bind(
    "<Return>",
    lambda event: send_command()
)

file_tab = tk.Frame(
    notebook
)

notebook.add(
    file_tab,
    text="File Browser"
)


file_frame = tk.Frame(
    file_tab
)

file_frame.pack(
    fill="x",
    padx=10,
    pady=10
)


tk.Label(
    file_frame,
    text="Path:"
).pack(
    side="left"
)


path_entry = tk.Entry(
    file_frame
)

path_entry.insert(
    0,
    "."
)

path_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)


tk.Button(
    file_frame,
    text="XEM FILE",
    command=view_files
).pack(
    side="left",
    padx=5
)


file_output = tk.Text(
    file_tab
)

file_output.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

task_tab = tk.Frame(
    notebook
)

notebook.add(
    task_tab,
    text="Task Manager"
)


task_frame = tk.Frame(
    task_tab
)

task_frame.pack(
    fill="x",
    padx=10,
    pady=10
)


tk.Button(
    task_frame,
    text="REFRESH",
    command=refresh_tasks
).pack(
    side="left"
)


tk.Label(
    task_frame,
    text="PID:"
).pack(
    side="left",
    padx=(20, 5)
)


pid_entry = tk.Entry(
    task_frame,
    width=15
)

pid_entry.pack(
    side="left"
)


tk.Button(
    task_frame,
    text="END TASK",
    command=end_task
).pack(
    side="left",
    padx=5
)


task_output = tk.Text(
    task_tab
)

task_output.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)

def close_window():

    if client is not None:
        disconnect_server()

    window.destroy()


window.protocol(
    "WM_DELETE_WINDOW",
    close_window
)

window.mainloop()
