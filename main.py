
from path_util import resource_path
import os
import logging
# logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
class Result:
    def __init__(self, result, periods):
        self.result = result
        self.periods = periods
class Main:
    def __init__(self):
        pass

    # def execute (self):
    #     p = Process(target=self.start, args=(), name='esms_communicator')
    #     p.start()
    
    def start(self):
        import socket
        import json
        from pathlib import Path
        from camera_controller import CameraController
        server_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_stream_socket.bind(("127.0.0.1", 12345))
        server_stream_socket.listen()
        camera = CameraController()
        logging.warning("Main: Waiting for connection ...")
        (connection, address) = server_stream_socket.accept()
        state = 'end'
        logging.warning("Main: Connected. Waiting for data ...")
        while True:
            msg = connection.recv(1024)
            msg = msg.decode('UTF-8')
            if msg != "":
                logging.warning("Main: data received...")
                logging.warning("Main: msg: {}".format(msg))
            if 'start' in msg:
                if state == 'end':
                    path = msg[6:]
                    Path(path).mkdir(parents=True, exist_ok=True)
                    state = 'start'
                    camera.set_video_path(path)
                    camera.start_camera()
                    connection.sendall(b"StreamPort:9090")
            elif 'end' in msg':
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
                    logging.warning("Main: msg sent")
if __name__ == "__main__":
    # os.environ['OPENH264_LIBRARY'] = resource_path('codec\openh264-1.8.0-win64.dll')
    logging.warning(f"Main: os.environ{os.environ['OPENH264_LIBRARY']}")
    main = Main()
    main.start()
