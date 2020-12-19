import time
from datetime import datetime
from Detection.Model.frame_info import FrameInfo
from Detection.Model.period_info import PeriodInfo
from Detection.Model.session_info import SessionInfo
NO_FACE_DETECTED = 7
ANGRY = 0
DISGUSTED = 1
FEARFUL = 2
HAPPY = 3
NEUTRAL = 4
SAD = 5
SURPRISED = 6
emotion_dict = {NO_FACE_DETECTED: "No face detected", ANGRY: "Angry", DISGUSTED: "Disgusted", FEARFUL: "Fearful", HAPPY: "Happy", 
NEUTRAL: "Neutral", SAD: "Sad", SURPRISED: "Surprised"}

# duration in miliseconds to be considered a valid emotion period
emotion_valid_duration = {
    NO_FACE_DETECTED: 4000, 
    ANGRY: 250, 
    DISGUSTED: 250, 
    FEARFUL: 250, 
    HAPPY: 500, 
    NEUTRAL: 1000, 
    SAD: 250, 
    SURPRISED: 500}
emotion_maximum_buffer_duration = {
    NO_FACE_DETECTED: 300, 
    ANGRY: 8000, 
    DISGUSTED: 400, 
    FEARFUL: 400, 
    HAPPY: 300, 
    NEUTRAL: 300, 
    SAD: 300, 
    SURPRISED: 300}

angry_duration = 15000
class EmotionStreamHandler:
    def __init__(self):
        self.frames = []
        self.current_frame = FrameInfo(None, None, None)
        self.previous_frame = FrameInfo(None, None, None)
        self.periods = []
        self.temp_durations = []
        for i in range (0, 8):
            self.periods.append([])
            self.temp_durations.append([0,0])
        self.session_begind = 0
        self.temp_time = 0
        self.count = 0
        self.warning = False
        self.warning_count = 0
    
    def add_frame(self, emotion):

        if self.session_begind == 0:
            self.session_begind = time.time()
        
        self.temp_time = time.time()
        
        passed_time = int(round((self.temp_time - self.session_begind)*1000))
        self.current_frame = FrameInfo(self.temp_time, passed_time, emotion)
        self.frames.append(self.current_frame)
        self.count+=1
        if self.previous_frame.timestamp is not None:
            for i in range(0, 8):
                duration = int(round((self.current_frame.timestamp - self.previous_frame.timestamp)*1000))
                if self.previous_frame.emotion == i and self.temp_durations[i] == [0,0]:
                    self.periods[i].append(PeriodInfo(self.previous_frame.timestamp, self.current_frame.timestamp, i))
                    self.temp_durations[i][0] += duration
                elif self.previous_frame.emotion == i and self.temp_durations[i] != [0,0]:
                    self.temp_durations[i][0] += duration
                    self.periods[i][len(self.periods[i])-1].period_end = self.current_frame.timestamp
                    self.periods[i][len(self.periods[i])-1].update()
                    self.temp_durations[i][1] = 0
                    if i == ANGRY:
                        if self.periods[i][len(self.periods[i])-1].duration >= angry_duration:
                            self.warning = True
                elif self.previous_frame.emotion != i and self.temp_durations[i] == [0,0]:
                    pass
                elif self.previous_frame.emotion != i and self.temp_durations[i] != [0,0]:
                    if self.temp_durations[i][0] >= emotion_valid_duration[i]:
                        self.temp_durations[i][1] += duration
                        if self.temp_durations[i][1] >= emotion_maximum_buffer_duration[i]:
                            self.temp_durations[i] = [0,0]
                            if self.warning == True:
                                if i == ANGRY:
                                    self.warning = False
                    else:                        
                        self.temp_durations[i] = [0,0]
                        duration = int(round((self.periods[i][len(self.periods[i])-1].period_end - self.periods[i][len(self.periods[i])-1].period_start)*1000))
                        del(self.periods[i][len(self.periods[i])-1])
        self.previous_frame = self.current_frame
    def finish(self):
        

        for i in range(0, len(self.periods)):
            if len(self.periods[i]) > 0:
                if self.periods[i][len(self.periods[i])-1].duration < emotion_valid_duration[i]:
                    del(self.periods[i][len(self.periods[i])-1])
        for period in self.periods[0]:
            if period.duration >= angry_duration:
                self.warning_count += 1
        # ****** print out all periods ******
        # for i in range(0, len(self.periods)):
        #     print("===={}==== size: {}".format(emotion_dict[i], len(self.periods[i])))
        #     for period in self.periods[i]:
        #         print(period.__dict__)
        #         duration = int(round((period.period_end - period.period_start)*1000))
        # print("__________________________________________________________________________________________")
        # print("__________________________________________________________________________________________")
        for periods in self.periods:
            for period in periods:
                period.period_start = int(round((period.period_start - self.session_begind)*1000))
                period.period_end = int(round((period.period_end - self.session_begind)*1000))
        session_info = SessionInfo(self.frames, self.session_begind, self.temp_time, self.periods, None) 
        return session_info