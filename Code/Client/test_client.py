import socket

HOST = "127.0.0.1"
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect((HOST, PORT))

print("Đã kết nối đến máy chủ.")

message = "Xin chào từ Client"

client_socket.sendall(message.encode("utf-8"))

print("Đã gửi dữ liệu đến máy chủ.")

response = client_socket.recv(1024)

message = response.decode("utf-8")

print("Phản hồi từ máy chủ:", message)

client_socket.close()