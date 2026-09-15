import tkinter as tk

def ask_permission(client_ip, client_port):
    result = False
    window = tk.Tk()
    window.title("Yêu cầu kết nối")
    window.geometry("400x180")
    window.resizable(False, False)

    label_title = tk.Label(
        window,
        text="YÊU CẦU KẾT NỐI",
        font=("Arial", 16, "bold")
    )
    label_title.pack(pady=15)

    label_client = tk.Label(
        window,
        text=f"Client {client_ip}:{client_port}\n"
             "yêu cầu kết nối Server",
        font=("Arial", 11)
    )
    label_client.pack(pady=5)
    button_frame = tk.Frame(window)
    button_frame.pack(pady=15)

    def allow():
        nonlocal result
        result = True
        window.destroy()
    def deny():
        nonlocal result
        result = False
        window.destroy()
    button_allow = tk.Button(
        button_frame,
        text="Cho phép",
        width=12,
        command=allow
    )
    button_allow.pack(side="left", padx=10)
    button_deny = tk.Button(
        button_frame,
        text="Từ chối",
        width=12,
        command=deny
    )
    button_deny.pack(side="left", padx=10)
    window.protocol(
        "WM_DELETE_WINDOW",
        deny
    )
    window.mainloop()

    return result