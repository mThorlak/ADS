import os
import shutil as su
import sys
import pandas as pd
from Serveur.rules_manager import rules as rules
from Serveur.sensor_manager import BufferFileModel as bfm
from Serveur.sensor_manager import SensorLogFileModel as slfm, ARCHIVE_LOG_PATH


# Step 1 : get path of the csv file
# Step 2 : set log instance with file property (priority, name, etc.)
# Step 3 : save the file (override if it already exists)
# Step 4 : check the buffer for keeping only the new lines
# Step 5 : manage the new lines of the file depending of the rules
# Step 6 : update the buffer
# Step 7 : register new lines in the 'all_logs.csv' file
# Step 8 : remove the log file from reception_log
# Step 9 : clear the buffer at the end of the day

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
    linesToAnalyzed = getLinesToAnalyzed(logToAnalyse)
    print("New lines to analyzed :")
    print(linesToAnalyzed)
    if linesToAnalyzed is not None:
        ### Step 5 ###
        print(" ############## Step 5 ##############")
        rules.run(logToAnalyse.pathFile, linesToAnalyzed)
        print("Rules has been processed")
        ### Step 6 ###
        print(" ############## Step 6 ##############")
        updateBuffer(logToAnalyse)
        print("Buffer updated")
        ### Step 7 ###
        print(" ############## Step 7 ##############")
        insertIntoBigDataLogFile(logToAnalyse)
        print("New lines inserted in all_logs.csv of the day")
    else:
        print("Nothing to analyse")
    ### Step 8 ###
    print(" ############## Step 8 ##############")
    deleteFile(sensorLogFileReceived)
    print(sensorLogFileReceived.pathFile + " has been deleted")
    ### Step 9 ###
    # print(" ############## Step 9 ##############")
    # clearBuffer()
    # print("Buffer cleaned")


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
    except Exception as err:
        # File already exists
        logSensorToCompare = logFileModel.content
        bigDataLogToCompare = pd.read_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv')
        logsToAdd = logSensorToCompare.merge(bigDataLogToCompare, how='left', indicator=True).loc[
            lambda x: x['_merge'] == 'left_only']
        header = ['ID', 'Date', 'Mac_Address']
        # Reindex for deleting _merge columns
        logsToAdd.reindex(header)
        print(logsToAdd)
        logsToAdd.to_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', mode='a', header=False,
                         index=False, columns=header)


# Return 1 if lines has been analyzed or 0 if never analyzed or None if no line to analyzed
def checkBuffer(logFileModel):
    bufferFile = bfm.BufferFileModel()
    lastRow = logFileModel.content.iloc[[-1]]
    newContentBuffer = {
        'Name': lastRow['ID'].item().split('-')[0],
        'Date': lastRow['Date'],
        'LastIndex': lastRow.iloc[[-1]].index.values[0]
    }
    rowInBuffer = bufferFile.content[bufferFile.content['Name'] == newContentBuffer['Name']]
    # If the sensor is not in the buffer file, the first line of the sensor's log file is return
    if rowInBuffer.empty:
        print("Not existing in buffer, start from the beginning...")
        return 0
    # Else, the line registered in the buffer file
    else:
        # Avoid to check line already analysed
        indexLogFileModel = logFileModel.content[logFileModel.content['Date'] == rowInBuffer['Date'].item()].iloc[[-1]]
        if newContentBuffer['LastIndex'] == indexLogFileModel.index.values[0]:
            print("Line already analysed")
            return None
        return 1


# Return all the new lines that needs to be analyzed
def getLinesToAnalyzed(logFileModel):
    checkBufferResult = checkBuffer(logFileModel)
    # Case where there is no more lines to analise
    if checkBufferResult is None:
        return None
    # Case where the log file was never analyzed
    elif checkBufferResult == 0:
        print("Never analyzed")
        return logFileModel.content
    # Case where there is lines to analise
    else:
        bufferFile = bfm.BufferFileModel()
        lineBufferFile = bufferFile.content.get(bufferFile.content['Name'] == logFileModel.content['ID'][0])
        print("Line buffer file :")
        print(lineBufferFile)
        indexWhereStart = lineBufferFile['LastIndex'].values[0]
        print(indexWhereStart)
        linesToAnalyzed = logFileModel.content.iloc[indexWhereStart + 1: logFileModel.content.index[-1] + 1]
        return linesToAnalyzed


# Update buffer file with the last line of the log file
def updateBuffer(logFileModel):
    bufferFile = bfm.BufferFileModel()
    # Get a line of the sensor file for checking if the sensor is already registered in the buffer file
    lastRow = logFileModel.content.iloc[[-1]]
    newContentBuffer = {
        'Name': lastRow['ID'].item().split('-')[0],
        'Date': lastRow['Date'],
        'LastIndex': lastRow.iloc[[-1]].index.values
    }
    dataFrame = pd.DataFrame(data=newContentBuffer)
    if newContentBuffer['Name'] in bufferFile.content['Name'].values:
        bufferFile.content = bufferFile.content[bufferFile.content.Name != newContentBuffer['Name']]
        bufferFile.content.to_csv(bufferFile.pathFile, mode='w', sep=',', header=True, index=False)
        dataFrame.to_csv(bufferFile.pathFile, mode='a', sep=',', header=False, index=False)
    else:
        dataFrame.to_csv(bufferFile.pathFile, mode='a', sep=',', header=False, index=False)


# Clear buffer content, keep only columns
def clearBuffer():
    bufferFile = bfm.BufferFileModel()
    bufferFile.content = bufferFile.content.iloc[0:0]
    bufferFile.content.to_csv(bufferFile.pathFile, mode='w', sep=',', header=True, index=False)


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
