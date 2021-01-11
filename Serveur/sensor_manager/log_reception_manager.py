import os
import shutil as su
import pandas as pd
from Serveur.sensor_manager import SensorLogFileModel as slfm, ARCHIVE_LOG_PATH, ACTUAL_DIRECTORY
from Serveur.sensor_manager import BufferFileModel as bfm


# Step 1 : get path of the csv file
# Step 2 : set log instance with file property (priority, name, etc.)
# Step 3 : save the file (override if it already exists)
# Step 4 : check the buffer for keeping only the new lines
# Step 5 : manage the new lines of the file depending of the rules
# Step 6 : update the buffer
# Step 7 : register new lines in the 'big log data' file

def runLogReceptionManager(pathFile):
    ### Step 1 and 2 ###
    sensorLogFileReceived = slfm.SensorLogFileModel(pathFile)
    ### Step 3 ###
    # logToAnalyse = archiveLogFile(sensorLogFileReceived.pathFile, sensorLogFileReceived.fileName, sensorLogFileReceived.dateLog)
    # TODO
    ### Step 4 ###
    linesToAnalyzed = getLinesToAnalyzed(sensorLogFileReceived)
    clearBuffer()
    ### Step 6 ###
    # updateBuffer(sensorLogFileReceived)
    ### Step 7 ###
    # insertIntoBigDataLogFile(sensorLogFileReceived)


# Archive log file send by sensor in archive log directory sort by day
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
        logsToAdd.to_csv(ARCHIVE_LOG_PATH + logFileModel.dateLog + '/all_logs.csv', mode='a', header=False,
                         index=False, columns=header)


# Return the last line (in dataFrame) analyzed before receiving the new sensor log file
def checkBuffer(logFileModel):
    bufferFile = bfm.BufferFileModel()
    lastRow = logFileModel.content.iloc[[-1]]
    newContentBuffer = {
        'Name': lastRow['ID'].item().split('-')[0],
        'Date': lastRow['Date'],
        'LastIndex': lastRow.iloc[[-1]].index.values
    }
    rowInBuffer = bufferFile.content[bufferFile.content['Name'] == newContentBuffer['Name']]
    # If the sensor is not in the buffer file, the first line of the sensor's log file is return
    if rowInBuffer.empty:
        return logFileModel.content.iloc[[0]]
    # Else, the line registered in the buffer file
    else:
        return logFileModel.content[logFileModel.content['Date'] == rowInBuffer['Date'].item()].iloc[0]


# Return all the new lines that needs to be analyzed
def getLinesToAnalyzed(logFileModel):
    checkBufferResult = checkBuffer(logFileModel)
    indexWhereStart = logFileModel.content[logFileModel.content['Date'] == checkBufferResult['Date']]
    # If more than one values, we take only the first index of the rows
    indexWhereStart = indexWhereStart.index.values[0]
    linesToAnalyzed = logFileModel.content.iloc[indexWhereStart: logFileModel.content.index[-1] + 1]
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


def run():
    # Example
    runLogReceptionManager(ACTUAL_DIRECTORY + '/reception_log/test2__10-12-2020.csv')
