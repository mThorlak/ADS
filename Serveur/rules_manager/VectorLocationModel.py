import os
import pandas as pd
from Serveur.rules_manager import VECTOR_LOCATION_PATH
from Serveur.api import service as service


class VectorLocationModel:
    pathFile = ""
    fileName = ""

    # Content -> dataFrame coming from the log file
    content = ""

    def __init__(self):
        self.pathFile = VECTOR_LOCATION_PATH
        self.fileName = os.path.basename(self.pathFile)
        self.content = pd.read_csv(self.pathFile)

    def getProperty(self):
        return "{ file path : " + self.pathFile + "; file name : " + self.fileName + ";} "

    def getContent(self):
        return self.content

    def createFile(self):
        service.createFile(self.pathFile)

    def flushFile(self):
        df = pd.DataFrame(columns=('Room', 'Content'))
        df.to_csv(self.pathFile, mode='w', sep=';', header=True, index=False)

    def getVectorsForRoom(self, room):
        return self.content.loc[self.content['Room'] == room]

