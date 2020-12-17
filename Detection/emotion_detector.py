import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
from path_util import resource_path
from threading import Thread
class EmotionDetector:

    def __init__(self, image):
        self.image = image
        self.model = Sequential()

        self.model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(48,48,1)))
        self.model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))
        self.model.add(Dropout(0.25))

        self.model.add(Flatten())
        self.model.add(Dense(1024, activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Dense(4, activation='softmax'))
        prediction = self.model.predict(self.image)
        self.emotion = int(np.argmax(prediction))

        print("model path: {}".format(resource_path("Detection\Weight\model-epoch-30.h5")))
        self.model.load_weights(resource_path("Detection\Weight\model-epoch-30.h5"))
        self.stopped = False
    
    def set_image(self, image):
        self.image = image
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
            prediction = self.model.predict(self.image)
            self.emotion = int(np.argmax(prediction))
    def get_emotion(self):
        # return the frame most recently read
        return self.emotion
    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
    