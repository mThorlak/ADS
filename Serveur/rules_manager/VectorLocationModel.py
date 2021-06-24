import ast
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
        self.content = pd.read_csv(self.pathFile, sep=';')

    def getProperty(self):
        return "{ file path : " + self.pathFile + "; file name : " + self.fileName + ";} "

    def getContent(self):
        return self.content

    def getContentDictionaryFormat(self):
        listVectors = self.getContent()
        vectorDictionary = {}
        i = 0
        for index, row in listVectors.iterrows():
            dictionary = {'Room': row['Room'], 'Content': ast.literal_eval(row['Content'])}
            vectorDictionary[index] = dictionary
            i = i + 1
        return vectorDictionary

    def createFile(self):
        service.createFile(self.pathFile)

    def flushFile(self):
        df = pd.DataFrame(columns=('Room', 'Content'))
        df.to_csv(self.pathFile, mode='w', sep=';', header=True, index=False)

    def getVectorsForRoom(self, room):
        return self.content.loc[self.content['Room'] == room]

    # Line format example => Salon; {'Salon': -60, 'Cuisine': -80}
    def insertValue(self, room, vector):
        data = [{'Room': room, 'Content': vector}]
        df = pd.DataFrame(data)
        df.to_csv(self.pathFile, mode='a', sep=';', header=False, index=False)

    def getVectorsForRoomDictionaryFormat(self, room):
        listVectors = self.getVectorsForRoom(room)
        vectorDictionary = {}
        i = 0
        for index, row in listVectors.iterrows():
            dictionary = {'Room': row['Room'], 'Content': ast.literal_eval(row['Content'])}
            vectorDictionary[index] = dictionary
            i = i + 1
        return vectorDictionary
