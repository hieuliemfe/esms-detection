import math
import json
from Detection.emotion_stream_handler import angry_duration as ANGRY_DURATION
NO_FACE_DETECTED_DURATION = 3*60*1000
emotion_dict = {7: "No face detected", 0: "Angry", 1: "Disgusted", 2: "Fearful", 3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised"}
ANGRY = 0
HAPPY = 1
NEUTRAL = 2
OTHER = 3
NO_FACE_DETECTED = 4
negative_emotions = [0, 1, 2, 5, 7]
positive_emotions = [3, 6]
positive_weight = 0.495
negative_weight = 0.505
class SessionEvaluator:
    def __init__(self):
        self.total_session_duration = 0
        self.emotions_duration = []
        self.emotions_period_count = []
        self.negative_emotions_duration = 0
        self.positive_emotions_duration = 0
        self.neutral_emotions_duration = 0
        self.no_face_detected_duration = 0
        self.negative_emotions_period_count = 0
        self.positive_emotions_period_count = 0
        self.neutral_emotion_period_count = 0
        self.no_face_detected_period_count = 0
        self.unidentified_period_duration = 0
        self.no_face_detected_warning = 0
        self.angry_warning = 0
        self.angry_duration_warning_max = 0
        self.no_face_detected_duration_warning_max = 0
        self.emotionless_warning = False
        self.emotion_level = 0
        for i in range(0, 5):
            self.emotions_duration.append(0)
            self.emotions_period_count.append(0)

    def modified_sigmoid(self, x):
        return round(2 / (1 + math.exp(-0.05*x)) -1, 6)

    def evaluate(self, session_info):
        result = ""
        self.total_session_duration = int(round((session_info.session_end - session_info.session_begin)*1000))
        for periods in session_info.periods:
            for period in periods:
                self.emotions_duration[period.emotion] += period.duration
                self.emotions_period_count[period.emotion] += 1
                if period.emotion in positive_emotions:
                    self.positive_emotions_duration += period.duration
                    self.positive_emotions_period_count += 1
                elif period.emotion in negative_emotions:
                    self.negative_emotions_duration += period.duration
                    self.negative_emotions_period_count += 1
                    if period.emotion == ANGRY:
                        if period.duration >= ANGRY_DURATION:
                            self.angry_warning += 1
                            if period.duration > self.angry_duration_warning_max:
                                self.angry_duration_warning_max = period.duration
                elif period.emotion == NEUTRAL:
                    self.neutral_emotions_duration += period.duration
                    self.neutral_emotion_period_count += 1
                elif period.emotion == NO_FACE_DETECTED:
                    self.no_face_detected_period_count += 1
                    self.no_face_detected_duration += period.duration
                    if period.duration >= NO_FACE_DETECTED_DURATION:
                        self.no_face_detected_warning += 1
                        if period.duration > self.no_face_detected_duration_warning_max:
                            self.no_face_detected_duration_warning_max = period.duration

        session_duration = int(round((session_info.session_end - session_info.session_begin)*1000))
        self.unidentified_period_duration = session_duration - (self.negative_emotions_duration + 
        self.positive_emotions_duration + self.unidentified_period_duration + 
        self.neutral_emotions_duration + self.no_face_detected_duration)
        if self.unidentified_period_duration < 0:
            self.unidentified_period_duration = 0
        total_duration_for_estimation = session_duration - (self.no_face_detected_duration + self.unidentified_period_duration)
        neutral_duration_percentage = self.neutral_emotions_duration / session_duration
        sum_negative_positive_duration = self.negative_emotions_duration + self.positive_emotions_duration
        score = 0
        tmp_negative_duration = self.negative_emotions_duration * negative_weight
        tmp_positive_duration = self.positive_emotions_duration * positive_weight
        # print("{} x {} = ".format(self.negative_emotions_duration, negative_weight))
        # print("temp neg: {}".format(tmp_negative_duration))
        # print("{} x {} = ".format(self.positive_emotions_duration, positive_weight))
        # print("temp pos: {}".format(tmp_positive_duration))
        sum_tmp_negative_positive_duration = tmp_negative_duration + tmp_positive_duration
        # print("tmp sum: {}".format(sum_tmp_negative_positive_duration))
        if neutral_duration_percentage < 0.50:
            if sum_negative_positive_duration != 0:
                negative_point = (tmp_negative_duration / sum_tmp_negative_positive_duration)*100
                positive_point = (tmp_positive_duration / sum_tmp_negative_positive_duration)*100
                # print("different: {}".format(positive_point - negative_point))
                score = self.modified_sigmoid(positive_point - negative_point)
        elif neutral_duration_percentage > 0.7:
            self.emotionless_warning = True
        session_info.emotion_level = score
        self.emotion_level = score
        # print("Session Duration: {}".format(session_duration))
        # for i in range(0, 5):
        #     print("=============================================")
        #     print("Emotion: {}".format(emotion_dict[i]))
        #     print("Total Duration: {}".format(self.emotions_duration[i]))
        #     print("Total period count: {}".format(self.emotions_period_count[i]))
        #     print("*********************************************")
        # print("Session Duration: {}".format(session_duration))
        # print("############### Negative emotion:")
        # print("Duration: {}".format(self.negative_emotions_duration))
        # print("Period Count: {}".format(self.negative_emotions_period_count))
        # print("############### Positive emotion:")
        # print("Duration: {}".format(self.positive_emotions_duration))
        # print("Period Count: {}".format(self.positive_emotions_period_count))
        # print("############### Neutral emotion:")
        # print("Duration: {}".format(self.neutral_emotions_duration))
        # print("Period Count: {}".format(self.neutral_emotion_period_count))
        # print("############### No face detected:")
        # print("Duration: {}".format(self.no_face_detected_duration))
        # print("Period Count: {}".format(self.no_face_detected_period_count))
        # print("############### Unidentified:")
        # print("Duration: {}".format(self.unidentified_period_duration))
        # print("_________________result:")
        # print(score)
        # print(self.__dict__)
        # return json.dumps(self.__dict__)
        return self

        
