import os
import pandas as pd
from Serveur.rules_manager import BUFFER_SENSORS_PATH


class BufferSensorsModel:
    pathFile = ""
    fileName = ""

    # Content -> dataFrame coming from the log file
    content = ""

    def __init__(self):
        self.pathFile = BUFFER_SENSORS_PATH
        self.fileName = os.path.basename(self.pathFile)
        self.content = pd.read_csv(self.pathFile, sep=',')

    def getProperty(self):
        return "{ file path : " + self.pathFile + "; file name : " + self.fileName + ";} "

    def getContent(self):
        return self.content
