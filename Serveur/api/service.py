import os as os
from Serveur.sensor_manager import ARCHIVE_LOG_PATH


# Get all the log dates by listing the name of the archiv_logs's subdirectories
def listDateLogs():
    directoryList = []
    for root, dirs, files in os.walk(ARCHIVE_LOG_PATH):
        directoryList.append(dirs)

    # [0] for returning only subdirectories
    return directoryList[0]
