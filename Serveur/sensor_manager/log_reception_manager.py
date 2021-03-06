import os
import shutil as su
import sys
import pandas as pd
from Serveur.rules_manager import rules as rules
from Serveur.sensor_manager import SensorLogFileModel as slfm, ARCHIVE_LOG_PATH


# Step 1 : get path of the csv file
# Step 2 : set log instance with file property (priority, name, etc.)
# Step 3 : save the file (override if it already exists)
# Step 4 : manage the new lines of the file depending of the rules
# Step 5 : register new lines in the 'all_logs.csv' file
# Step 6 : remove the log file from reception_log

def runLogReceptionManager(pathFile):
    ### Step 1 and 2 ###
    sensorLogFileReceived = slfm.SensorLogFileModel(pathFile)
    print(" ############## Step 1 and 2 ##############")
    print("File instance created for : " + sensorLogFileReceived.pathFile)
    ### Step 3 ###
    print(" ############## Step 3 ##############")
    logToAnalyse = archiveLogFile(sensorLogFileReceived.pathFile, sensorLogFileReceived.fileName, sensorLogFileReceived.dateLog)
    logToAnalyse = slfm.SensorLogFileModel(logToAnalyse)
    print("Log file + " + logToAnalyse.fileName + " registered and archived")
    ### Step 4 ###
    print(" ############## Step 4 ##############")
    rules.run(logToAnalyse.pathFile, logToAnalyse.content)
    print("Rules has been processed")
    ### Step 5 ###
    print(" ############## Step 5 ##############")
    insertIntoBigDataLogFile(logToAnalyse)
    print("New lines inserted in all_logs.csv of the day")
    ### Step 6 ###
    print(" ############## Step 6 ##############")
    deleteFile(sensorLogFileReceived)
    print(sensorLogFileReceived.pathFile + " has been deleted")


# Archive log file send by sensor in archive log directory sort by day and return the path of the file registered
def archiveLogFile(pathFileToCopy, newFileName, dateLog):
    newPathFileRegistered = ARCHIVE_LOG_PATH + '/' + dateLog + '/' + newFileName
    try:
        os.mkdir(ARCHIVE_LOG_PATH + '/' + dateLog)
        su.copy(pathFileToCopy, newPathFileRegistered)
        return newPathFileRegistered
    except Exception:
        su.copy(pathFileToCopy, newPathFileRegistered)
        return newPathFileRegistered


# Insert new data from sensor log into the big data log file
def insertIntoBigDataLogFile(logFileModel):
    # Check if big log file already exists
    try:
        # If it is not exists, create it with data of the sensor logs
        open(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', "x")
        logFileModel.content.to_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', index=False)
    except Exception:
        # File already exists
        logFileModel.content.to_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', mode='a', index=False,
                                    header=False)


# Delete file given in parameter
def deleteFile(sensorLogFileReceived):
    try:
        os.remove(sensorLogFileReceived.pathFile)
        print(sensorLogFileReceived.pathFile + " removed")
    except OSError as e:
        print("Error: %s : %s" % (sensorLogFileReceived.fileName, e.strerror))


def run():
    print(sys.argv[1])
    # Example
    # clearBuffer()
    # runLogReceptionManager(ACTUAL_DIRECTORY + '/reception_log/test1__10-12-2020.csv')
