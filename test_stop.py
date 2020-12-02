import socket
server_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_stream_socket.connect(("127.0.0.1", 12345))
server_stream_socket.send(b"exit")
msg = server_stream_socket.recv(1024)
print(msg)
server_stream_socket.close()
