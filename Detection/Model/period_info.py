class PeriodInfo:  
    def __init__(self, period_start, period_end, emotion):  
        self.period_start = period_start
        self.period_end = period_end
        self.emotion = emotion
        self.duration = int(round((self.period_end-self.period_start)*1000))

    def update(self):
        self.duration = int(round((self.period_end-self.period_start)*1000))