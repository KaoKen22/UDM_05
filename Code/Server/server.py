import socket

HOST = "0.0.0.0"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind((HOST, PORT))
server_socket.listen(5)

print("Máy chủ đang chạy tại cổng", PORT)
print("Đang chờ máy khách kết nối...")

client_socket, client_address = server_socket.accept()

print("Máy khách đã kết nối:", client_address)

data = client_socket.recv(1024)

message = data.decode("utf-8")

print("Nhận được từ máy khách:", message)

response = "Máy chủ đã nhận được dữ liệu."

client_socket.sendall(response.encode("utf-8"))

print("Đã gửi phản hồi cho máy khách.")

client_socket.close()
server_socket.close()