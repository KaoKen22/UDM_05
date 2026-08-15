import tkinter as tk
import socket

client = None

def connect_server():
    global client

    ip = ip_entry.get()
    port = int(port_entry.get())

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))

        status_label.config(text="Đã kết nối Server")

    except:
        status_label.config(text="Kết nối thất bại")
        client = None

def disconnect_server():
    global client

    if client != None:
        client.close()
        client = None

    status_label.config(text="Đã ngắt kết nối")

window = tk.Tk()
window.title("TCP Client")
window.geometry("400x300")

tk.Label(
    window,
    text="TCP CLIENT",
    font=("Arial", 18)
).pack(pady=20)

tk.Label(window, text="Server IP").pack()

ip_entry = tk.Entry(window)
ip_entry.insert(0, "127.0.0.1")
ip_entry.pack()

tk.Label(window, text="Port").pack()

port_entry = tk.Entry(window)
port_entry.insert(0, "5000")
port_entry.pack()

tk.Button(
    window,
    text="CONNECT",
    command=connect_server
).pack(pady=10)

tk.Button(
    window,
    text="DISCONNECT",
    command=disconnect_server
).pack()

status_label = tk.Label(
    window,
    text="Chưa kết nối"
)

status_label.pack(pady=15)

window.mainloop()