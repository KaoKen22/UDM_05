import socket


def connect_server(ip, port):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))

        return client

    except:
        return None


def disconnect_server(client):
    if client != None:
        client.close()