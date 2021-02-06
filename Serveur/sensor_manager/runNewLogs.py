import os
import time
from Serveur.sensor_manager import RECEPTION_LOG_PATH
from Serveur.sensor_manager import log_reception_manager


def runNewLog():
    while True:
        if len(os.listdir(RECEPTION_LOG_PATH)) == 0:
            print("No log received")
        else:
            print("--------------- Log received ! -----------------")
            listFiles = listLogsReceived()
            for file in listFiles:
                log_reception_manager.runLogReceptionManager(RECEPTION_LOG_PATH + file)

        time.sleep(2)


# Get all the log received in reception log
def listLogsReceived():
    directoryList = []
    for root, dirs, files in os.walk(RECEPTION_LOG_PATH):
        directoryList.append(files)
    # [1] for returning only files
    return directoryList[0]
