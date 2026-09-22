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
    ACTION_DISCONNECT,
    build_execute_request,
    build_list_dir_request,
    build_request,
    parse_response
)

client = None

def receive_data():

    data = b""

    client.settimeout(0.5)

    try:
        while True:
            part = client.recv(4096)

            if not part:
                break

            data += part

    except socket.timeout:
        pass

    except Exception:
        pass

    client.settimeout(None)

    return data.decode(
        "utf-8",
        errors="ignore"
    )

def connect_server():

    global client

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

        client.connect(
            (ip, port)
        )

        status_label.config(
            text="Đã kết nối Server"
        )

        terminal.insert(
            tk.END,
            "Đã kết nối Server.\n"
        )

        terminal.see(tk.END)

    except Exception as error:

        if client is not None:
            client.close()

        client = None

        status_label.config(
            text="Kết nối thất bại"
        )

        terminal.insert(
            tk.END,
            "Kết nối thất bại: "
            + str(error)
            + "\n"
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

    terminal.insert(
        tk.END,
        "Đã ngắt kết nối.\n"
    )

    terminal.see(tk.END)


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

def send_command():

    if client is None:

        terminal.insert(
            tk.END,
            "Chưa kết nối Server.\n"
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
                "[ERROR] Không nhận được phản hồi.\n"
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

    if client is None:

        file_text.insert(
            tk.END,
            "Chưa kết nối Server.\n"
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
                "[ERROR] Không nhận được phản hồi.\n"
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

    if client is None:

        task_text.insert(
            tk.END,
            "Chưa kết nối Server.\n"
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
                "[ERROR] Không nhận được phản hồi.\n"
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

    if client is None:

        task_text.insert(
            tk.END,
            "Chưa kết nối Server.\n"
        )

        return

    pid = pid_entry.get().strip()

    if pid == "":

        task_text.insert(
            tk.END,
            "Vui lòng nhập PID.\n"
        )

        return

    if not pid.isdigit():

        task_text.insert(
            tk.END,
            "PID phải là số.\n"
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
                "[ERROR] Không nhận được phản hồi.\n"
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
    text="Chưa kết nối"
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


tk.Button(
    command_frame,
    text="SEND",
    command=send_command
).pack(
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
    text="Đường dẫn:"
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


tk.Button(
    path_frame,
    text="XEM FILE",
    command=view_files
).pack(
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


tk.Button(
    task_tab,
    text="REFRESH",
    command=refresh_tasks
).pack(
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


tk.Button(
    pid_frame,
    text="END TASK",
    command=end_task
).pack(
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




def close_window():

    if client is not None:
        disconnect_server()

    window.destroy()


window.protocol(
    "WM_DELETE_WINDOW",
    close_window
)




window.mainloop()
