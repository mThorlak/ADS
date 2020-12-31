import os
import pandas as pd


class SensorAllLogsFileModel:
    dateLog = ""
    pathFile = ""
    fileName = ""

    # Content -> dataFrame coming from the log file
    content = ""

    def __init__(self, path):
        self.pathFile = path
        self.fileName = os.path.basename(self.pathFile)
        self.dateLog = os.path.dirname(self.pathFile)
        self.content = pd.read_csv(self.pathFile, sep=',')

    def getProperty(self):
        return "{ file path : " + self.pathFile + "; file name : " + self.fileName + ";  date log : " + self.dateLog + \
               "} "

    def getContent(self):
        return self.content

    def getDateLog(self):
        return self.dateLog
