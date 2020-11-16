from camera_controller import CameraController
from pathlib import Path
import socket
import json
server_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_stream_socket.bind(("127.0.0.1", 12345))
server_stream_socket.listen()
camera = CameraController()
(connection, address) = server_stream_socket.accept()
class Result:
    def __init__(self, result, periods):
        self.result = result
        self.periods = periods
print("Waiting for connection ...")

state = 'end'
print("Connected. Waiting for data ...")
while True:
    msg = connection.recv(1024)
    msg = msg.decode('UTF-8')
    if msg != "":
        print(msg)
    if 'start' in msg:
        if state == 'end':
            path = msg[6:]
            Path(path).mkdir(parents=True, exist_ok=True)
            state = 'start'
            camera.set_video_path(path)
            camera.start_camera()
            connection.sendall(b"StreamPort:9090")
    elif msg == "end":
        print(msg)
        if state == 'start':
            state = 'end'
            camera.stop_camera()
            while True:
                if camera.finished is True:
                    camera.finished = False
                    break
            periods = []
            for i in range(0, 8):
                sp = []
                for period in camera.session_info.periods[i]:
                    sp.append(period.__dict__)
                periods.append(sp)
            result = Result(camera.result.__dict__, periods)
            json_string = json.dumps(result.__dict__)
            connection.sendall(f"SessionResult:{json_string}".encode('UTF-8'))
