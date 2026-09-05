import tkinter as tk
from tkinter import ttk
import socket

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

    except:
        pass

    client.settimeout(None)

    return data.decode("utf-8", errors="ignore")


def connect_server():
    global client

    ip = ip_entry.get()
    port = int(port_entry.get())

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))

        status_label.config(text="Đã kết nối Server")
        terminal.insert(tk.END, "Đã kết nối Server.\n")

    except:
        status_label.config(text="Kết nối thất bại")
        client = None


def disconnect_server():
    global client

    if client != None:
        client.close()
        client = None

    status_label.config(text="Đã ngắt kết nối")
    terminal.insert(tk.END, "Đã ngắt kết nối.\n")


def send_command():

    if client == None:
        terminal.insert(tk.END, "Chưa kết nối Server.\n")
        return

    command = command_entry.get()

    if command == "":
        return

    try:
        terminal.insert(tk.END, "> " + command + "\n")

        client.send(command.encode("utf-8"))

        result = receive_data()

        terminal.insert(tk.END, result + "\n")
        terminal.see(tk.END)

        command_entry.delete(0, tk.END)

    except:
        terminal.insert(tk.END, "Lỗi gửi lệnh.\n")


def view_files():

    if client == None:
        file_text.insert(tk.END, "Chưa kết nối Server.\n")
        return

    path = path_entry.get()

    if path == "":
        path = "."

    try:
        command = 'dir "' + path + '"'

        client.send(command.encode("utf-8"))

        result = receive_data()

        file_text.delete("1.0", tk.END)
        file_text.insert(tk.END, result)
        file_text.see(tk.END)

    except:
        file_text.insert(tk.END, "Lỗi xem file.\n")

def refresh_tasks():

    if client == None:
        task_text.insert(tk.END, "Chưa kết nối Server.\n")
        return

    try:
        client.send("tasklist".encode("utf-8"))

        result = receive_data()

        task_text.delete("1.0", tk.END)
        task_text.insert(tk.END, result)
        task_text.see(tk.END)

    except:
        task_text.insert(tk.END, "Lỗi lấy danh sách Task.\n")


def end_task():

    if client == None:
        task_text.insert(tk.END, "Chưa kết nối Server.\n")
        return

    pid = pid_entry.get()
    if pid == "":
        task_text.insert(tk.END, "Vui lòng nhập PID.\n")
        return

    try:
        command = "taskkill /PID " + pid + " /F"

        client.send(command.encode("utf-8"))

        result = receive_data()

        task_text.insert(tk.END, "\n" + result + "\n")
        task_text.see(tk.END)

        pid_entry.delete(0, tk.END)

    except:
        task_text.insert(tk.END, "Lỗi End Task.\n")


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

ip_entry.insert(
    0,
    "127.0.0.1"
)

ip_entry.pack()


tk.Label(
    window,
    text="Port"
).pack()

port_entry = tk.Entry(window)

port_entry.insert(
    0,
    "5000"
)

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


file_tab = tk.Frame(tabs)

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

path_frame = tk.Frame(file_tab)

path_frame.pack(
    fill="x",
    padx=10
)

path_entry = tk.Entry(path_frame)

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

file_text = tk.Text(file_tab)

file_text.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


task_tab = tk.Frame(tabs)

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

pid_frame = tk.Frame(task_tab)

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
).pack(
    side="right"
)

task_text = tk.Text(task_tab)

task_text.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=5
)
window.mainloop()
