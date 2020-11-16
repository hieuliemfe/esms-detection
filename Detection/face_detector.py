# import the necessary packages
from threading import Thread
from path_util import resource_path
import cv2
class FaceDetector:
    def __init__(self, frame):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.frame = frame
        self.facecasc = cv2.CascadeClassifier(resource_path('Detection\haarcascade_frontalface_default.xml'))
        self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.faces = self.facecasc.detectMultiScale(self.gray,scaleFactor=1.3, minNeighbors=5)
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
    def set_frame(self, frame):
        self.frame = frame
    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self
    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            self.gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            self.faces = self.facecasc.detectMultiScale(self.gray,scaleFactor=1.3, minNeighbors=5)
    def get_faces(self):
        # return the frame most recently read
        return self.faces
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True