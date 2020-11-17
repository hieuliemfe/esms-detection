from Detection.emotion_detector import EmotionDetector
from Detection.emotion_stream_handler import EmotionStreamHandler
from Detection.Model.frame_info import FrameInfo
from Detection.Model.session_info import SessionInfo
from Detection.session_evaluator import SessionEvaluator
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from Detection.face_detector import FaceDetector
import time
import cv2
import numpy as np
from path_util import resource_path
import json
import socket
import threading
import base64

# prevents openCL usage and unnecessary logging messages
cv2.ocl.setUseOpenCL(False)

# dictionary which assigns each label an emotion (alphabetical order)
emotion_dict = {7: "No face detected", 0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
class AngryPeriods:
    def __init__(self, periods):
        self.periods = periods
class FrameStreamInfo:
    def __init__(self, img_src, is_warning, emotion):
        self.img_src = img_src
        self.is_warning = is_warning
        self.emotion = emotion
class CameraController:
    def __init__(self):
        self.video_out = "temp_vid"
        self.video_out_width = 400
        self.video_out_height = 300
        self.video_out_fps = 20
        self.cap_device = 0
        self.is_stop = False
        self.stream_port = 9090
        self.session_info = SessionInfo(None, None, None, None, None)
        self.result = None
        self.periods = None
        self.stream_handler = EmotionStreamHandler()
        self.finished = False
    def encode_img(self, img):
        """Encodes an image as a png and encodes to base 64 for display."""
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        success, encoded_img = cv2.imencode('.jpg', img, encode_param)
        if success:
            return base64.b64encode(encoded_img).decode('UTF-8')
        return ''
    def set_video_path(self, path):
        self.video_out = path
    def set_video_out_specs(self, width, height, fps):
        self.video_out_width = width
        self.video_out_height = height
        self.video_out_fps = fps
    def set_camera_device(self, device):
        self.cap_device = device
    def start_camera(self):
        print('start_camera called')
        self.is_stop = False
        self.stream_handler = EmotionStreamHandler()
        self.detect_thread = threading.Thread(target=self.detect_from_camera, daemon=True)
        self.detect_thread.start()
    def stop_camera(self):
        self.is_stop = True
    def detect_from_camera(self):
        video_path = self.video_out + "video.mp4"
        print("Path: {}".format(video_path))
        video_writer = cv2.VideoWriter(
            video_path, cv2.VideoWriter_fourcc(*'avc1'), self.video_out_fps, (self.video_out_width, self.video_out_height))
        print('detect_from_camera called')
        cap = WebcamVideoStream(src=0).start()
        fps_evaluator = FPS().start()
        face_detector = None
        emotion_detector = None

        print('make socket')
        server_stream_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_stream_socket.bind(("127.0.0.1", self.stream_port))
        server_stream_socket.listen()
        print('Waiting for connection')
        while True:
            start_time = time.time()
            (connection, address) = server_stream_socket.accept()
            hasFace = False
            frame = cap.read()

            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = None
            if face_detector == None:
                face_detector = FaceDetector(frame)
                face_detector.start()
            else:
                face_detector.set_frame(frame)
            faces = face_detector.get_faces()
            frameInfo = FrameInfo(None, None, None)

            for (x, y, w, h) in faces:
                hasFace = True
                # cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (255, 0, 0), 2)
                roi_gray = gray[y:y + h, x:x + w]
                cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray, (48, 48)), -1), 0)
                if emotion_detector is None:
                    emotion_detector = EmotionDetector(cropped_img)
                    emotion_detector.start()
                else:
                    emotion_detector.set_image(cropped_img)
                maxindex = emotion_detector.get_emotion()
                # cv2.putText(frame, emotion_dict[maxindex], (x+20, y-60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                self.stream_handler.add_frame(maxindex)
            if hasFace is not True:
                self.stream_handler.add_frame(7)
            # cv2.imshow('Video', cv2.resize(frame,(1600,960),interpolation = cv2.INTER_CUBIC))
            img = cv2.resize(frame,(self.video_out_width,self.video_out_height),interpolation = cv2.INTER_CUBIC)
            video_writer.write(img)

            img_src = self.encode_img(img)
            frame_stream_info = FrameStreamInfo(img_src, self.stream_handler.warning, self.stream_handler.current_frame.emotion)
            connection.sendall(json.dumps(frame_stream_info.__dict__).encode('UTF-8'))
            connection.close()
            fps_evaluator.update()
            if self.is_stop is True:
                self.session_info = self.stream_handler.finish()
                if emotion_detector is not None:
                    emotion_detector.stop()
                if face_detector is not None:
                    face_detector.stop()
                fps_evaluator.stop()
                cap.stop()
                video_writer.release()
                
                print("[INFO] elasped time: {:.2f}".format(fps_evaluator.elapsed()))
                print("[INFO] approx. FPS: {:.2f}".format(fps_evaluator.fps()))
                with open(self.video_out + 'video_info.json', 'w') as outfile:
                    json.dump([frame_obj.__dict__ for frame_obj in self.session_info.frames], outfile)
                angry_period = AngryPeriods(self.session_info.periods[0])
                # self.periods = json.dumps([[ob.__dict__ for ob in lst] for lst in self.session_info.periods])
                with open(self.video_out + 'periods_info.json', 'w') as outfile:
                    json.dump([period_obj.__dict__ for period_obj in self.session_info.periods[0]], outfile)    
                break
            end_time = time.time()
            wait_time = (0.05-(end_time - start_time)-0.005)
            if wait_time < 0:
                wait_time = 0
            time.sleep(wait_time)
        session_evaluator = SessionEvaluator()
        result = session_evaluator.evaluate(self.session_info)
        result.angry_warning = self.stream_handler.warning_count
        self.result = result
        # print("#*#*#*#*# Result:")
        # print(self.result)
        # for i in range(0, len(self.session_info.periods)):
        #     print("===={}==== size: {}".format(emotion_dict[i], len(self.session_info.periods[i])))
        #     for period in self.session_info.periods[i]:
        #         print(period.__dict__)
        #         duration = int(round((period.period_start - period.period_end)*1000))
        cv2.destroyAllWindows()
        self.finished = True
