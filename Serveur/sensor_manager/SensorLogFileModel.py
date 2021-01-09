import os
import pandas as pd


class SensorLogFileModel:
    sensorName = ""
    dateLog = ""
    pathFile = ""
    fileName = ""

    # Content -> dataFrame coming from the log file
    content = ""

    def __init__(self, path):
        self.pathFile = path
        self.fileName = os.path.basename(self.pathFile)
        self.sensorName = self.fileName.split('__')[0]
        self.dateLog = self.fileName.split('__')[1]
        self.dateLog = self.dateLog.split('.csv')[0]
        self.content = pd.read_csv(self.pathFile)

    def getProperty(self):
        return "{ file path : " + self.pathFile + "; sensor name : " + self.sensorName + \
               ";  date log : " + self.dateLog + " }"

    def getContent(self):
        return self.content

    def getSensorName(self):
        return self.sensorName

    def getDateLog(self):
        return self.dateLog
