import socket
import json
while True:
    server_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_stream_socket.connect(("127.0.0.1", 9090))
    try:
        # length = int(server_stream_socket.recv(1024).decode('UTF-8'))
        # print(length)
        msg = server_stream_socket.recv(999999).decode('UTF-8')
        print("+1")
        text_file = open("image.json", "w")

        text_file.write(msg)

        text_file.close()
        server_stream_socket.close()
    except:
        server_stream_socket.close()
        pass
