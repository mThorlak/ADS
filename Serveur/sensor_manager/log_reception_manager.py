import os
import shutil as su
import pandas as pd
from Serveur.sensor_manager import SensorLogFileModel as slfm, ARCHIVE_LOG_PATH, ACTUAL_DIRECTORY


# Step 1 : get path of the csv file
# Step 2 : set log instance with file property (priority, name, etc.)
# Step 3 : save the file (override if it already exists)
# Step 4 : manage the file depending of the rules
# Step 5 : register new lines in the 'big log data' file

def runLogReceptionManager(pathFile):
    # Step 1 and 2
    logFileModel = slfm.SensorLogFileModel(pathFile)
    # Step 3
    archiveLogFile(logFileModel.pathFile, logFileModel.fileName, logFileModel.dateLog)
    # Step 5
    insertIntoBigDataLogFile(logFileModel)


# Archive log file send by sensor in archive log directory sort by day
def archiveLogFile(pathFileToCopy, newFileName, dateLog):
    try:
        os.mkdir(ARCHIVE_LOG_PATH + '/' + dateLog)
        su.copy(pathFileToCopy, ARCHIVE_LOG_PATH + '/' + dateLog + '/' + newFileName)
    except Exception as err:
        su.copy(pathFileToCopy, ARCHIVE_LOG_PATH + '/' + dateLog + '/' + newFileName)


def insertIntoBigDataLogFile(logFileModel):
    # Check if big log file already exists
    try:
        # If it is not exists, create it with data of the sensor logs
        open(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', "x")
        logFileModel.content.to_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', index=False)
    except Exception as err:
        # File already exists
        logSensorToCompare = logFileModel.content
        bigDataLogToCompare = pd.read_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv')
        logsToAdd = logSensorToCompare.merge(bigDataLogToCompare, how='left', indicator=True).loc[
            lambda x: x['_merge'] == 'left_only']
        header = ['ID', 'Date', 'Mac_Address']
        # Reindex for deleting _merge columns
        logsToAdd.reindex(header)
        logsToAdd.to_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', mode='a', header=False,
                         index=False, columns=header)


def run():
    runLogReceptionManager(ACTUAL_DIRECTORY + '/reception_log/test2__10-12-2020.csv')
