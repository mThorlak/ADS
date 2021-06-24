from datetime import datetime
import Serveur.api.service as service
from Serveur.sensor_manager import SensorLogFileModel as slfm, ARCHIVE_LOG_PATH
from Serveur.rules_manager import SensorConfigModel as scm
from Serveur.rules_manager import VectorLocationModel as vlm
from Serveur.sensor_manager import SensorAllLogsFileModel as salfm


# Get RSSI range of a specified config sensor
def getRssiRange(pathFile):
    logConfigSensor = scm.SensorConfigModel()
    logConfigSensor.content.set_index('Name', inplace=True)
    logSensor = slfm.SensorLogFileModel(pathFile)
    resultSearch = logConfigSensor.content.loc[logSensor.sensorName]
    return resultSearch['Max_Range']


# Sort that received signal from the specified mac_address during the last 15 seconds
# Return example : [['Test8-02', '2020-13-10T21:39:10Z', 'A1:B5:R1:N1:B9', -60],
# ['Test3-01', '2020-13-10T21:38:20Z', 'A1:B5:R1:N1:B9', -40],
# ['Test4-05', '2020-13-10T21:39:03Z', 'A1:B5:R1:N1:B9', -50]]
def sortLogsInTheGoodTimeRange(macAddress, date, isInitialisation):
    date = date[:-1]
    dateConverter = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    # Get the date without the time for finding the good "all logs" file
    dateOfTheDay = dateConverter.date().strftime("%d-%m-%Y")
    allTodayLogsMacAddress = service.getLogsByDateAndMacAddress(dateOfTheDay, macAddress)
    allTodayLogsMacAddressList = allTodayLogsMacAddress.values.tolist()
    dateLogs = []
    # Collect all dates and removing the "Z" at the end
    for logs in allTodayLogsMacAddressList:
        dateTmp = logs[1]
        dateTmp = dateTmp[:-1]
        dateLogs.append(dateTmp)
    # Check all the times and get the ones which are in the last 15 seconds
    i = 0
    storeIndex = []
    # Keep only the ones equal or later than the date given in parameter
    while i < len(dateLogs):
        dateConverted = datetime.strptime(dateLogs[i], '%Y-%m-%dT%H:%M:%S')
        if isInitialisation:
            if dateConverted.time() < dateConverter.time():
                i = i + 1
                continue
            else:
                timeSubtracted = (dateConverted - dateConverter).seconds
        # If not an initialisation by the installer, we check logs in the before and after 15 seconds
        else:
            if dateConverted.time() < dateConverter.time():
                timeSubtracted = (dateConverter - dateConverted).seconds
            else:
                timeSubtracted = (dateConverted - dateConverter).seconds
        # Collect only the logs similar in a 15 seconds range
        if timeSubtracted <= 15:
            storeIndex.append(i)
        i = i + 1
    result = []
    for i in storeIndex:
        result.append(allTodayLogsMacAddressList[i])
    return result


# Sort list of logs with the good RSSI range
# Return example : [['Test8-02', '2020-13-10T21:39:10Z', 'A1:B5:R1:N1:B9', -60],
# ['Test3-01', '2020-13-10T21:38:20Z', 'A1:B5:R1:N1:B9', -40]]
def sortLogsInTheGoodRssiRange(listOfLogsInTheGoodTimeRange):
    listSortedWithGoodRssiRange = []
    sensorConfigModel = scm.SensorConfigModel()
    i = 0
    while i < len(listOfLogsInTheGoodTimeRange):
        sensorNameLog = listOfLogsInTheGoodTimeRange[i][0]
        rssiLog = listOfLogsInTheGoodTimeRange[i][3]
        # Find the good sensor config for getting the min and max RSSI range
        for sensorConfigName in sensorConfigModel.content["Name"].values:
            # I found, check the log RSSI value is in the range accepted by the config sensor
            if str(sensorConfigName).capitalize() in sensorNameLog:
                sensorConfig = sensorConfigModel.content.loc[sensorConfigModel.content["Name"] == sensorConfigName] \
                    .values.tolist()
                maxRange = sensorConfig[0][4]
                if rssiLog >= maxRange:
                    listSortedWithGoodRssiRange.append(listOfLogsInTheGoodTimeRange[i])
        i = i + 1
    return listSortedWithGoodRssiRange


# Delete duplicate log and change for example Salon-01 to Salon
# Result example :
# [['Test2', '2020-12-10T20:38:40Z', 'A1:B5:R1:N1:B9', -1], ['Test8', '2020-12-10T20:38:50Z', 'A1:B5:R1:N1:B9', -4]]
def deleteDuplicateLogAndGetRoomName(listOfLogs):
    logsRoomNameFormatted = []
    sensorConfigModel = scm.SensorConfigModel()
    for log in listOfLogs:
        for sensorConfigName in sensorConfigModel.content["Name"].values:
            if str(sensorConfigName).capitalize() in log[0]:
                log[0] = str(sensorConfigName).capitalize()
                logsRoomNameFormatted.append(log)
    if len(logsRoomNameFormatted) <= 1:
        return logsRoomNameFormatted
    else:
        logsWithoutDuplicate = []
        for log in logsRoomNameFormatted:
            isDuplicate = False
            i = 0
            if len(logsWithoutDuplicate) == 0:
                logsWithoutDuplicate.append(log)
                continue
            while i < len(logsWithoutDuplicate):
                if log[0] in logsWithoutDuplicate[i][0]:
                    isDuplicate = True
                i = i + 1
            if not isDuplicate:
                logsWithoutDuplicate.append(log)
        return logsWithoutDuplicate


# Get all sensors that received signal from the specified mac_address at the same time,
# and calculate the distance between us
# Here is a list example : {'Test3-01': 1, 'Test8-02': 59, 'Test4-05': 49}
# The first one is ever the best RSSI
def calculateEuclideanDistance(listOfLogsSorted):
    # Get the best RSSI
    bestRSSI = -500
    indexOfBestRSSI = 0
    i = 0
    for logs in listOfLogsSorted:
        rssiLogs = logs[3]
        if rssiLogs > bestRSSI:
            bestRSSI = rssiLogs
            indexOfBestRSSI = i
        i = i+1
    # Now we calculate the distance between each logs and store its in a list
    listDistance = {listOfLogsSorted[indexOfBestRSSI][0]: 1}
    i = 0
    while i < len(listOfLogsSorted):
        if i == indexOfBestRSSI:
            i = i + 1
            continue
        distance = (listOfLogsSorted[i][3] * -1) - 1
        listDistance[listOfLogsSorted[i][0]] = distance
        i = i + 1
    return listDistance


# Return a list with the
# {'Test3-01': ['Test3-01', '2020-13-10T21:38:20Z', 'A1:B5:R1:N1:B9', 1, 'Garage'],
# 'Test8-02': ['Test8-02', '2020-13-10T21:39:10Z', 'A1:B5:R1:N1:B9', 59, 'Cuisine'],
# 'Test4-05': ['Test4-05', '2020-13-10T21:39:03Z', 'A1:B5:R1:N1:B9', 49, 'Salon']}
def determineLocation(listDistance, date):
    # Get the good all logs file
    date = date[:-1]
    dateConverter = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    dateOfTheDay = dateConverter.date().strftime("%d-%m-%Y")
    pathFile = ARCHIVE_LOG_PATH + dateOfTheDay + '/all_logs.csv'
    allLogsFileModel = salfm.SensorAllLogsFileModel(pathFile)
    sensorConfigModel = scm.SensorConfigModel()
    result = {}
    for i in listDistance:
        log = allLogsFileModel.content.loc[allLogsFileModel.content['ID'] == str(i)].values.tolist()
        log = log[0]
        log[3] = listDistance[i]
        for nameSensor in sensorConfigModel.content["Name"].values:
            if str(nameSensor).capitalize() in log[0]:
                sensorConfig = sensorConfigModel.content.loc[sensorConfigModel.content["Name"] == nameSensor]\
                    .values.tolist()
                roomDescription = sensorConfig[0][3]
                log.append(roomDescription)
        result[i] = log
    return result


# Create a message to send in string format
def displayLocation(listLocation):
    # listLocation :
    # Key and 0 => sensorIDLog
    # 1 => Date log
    # 2 => Mac address
    # 3 => RSSI
    # 4 => Room description
    i = 0
    response = ""
    for sensor in listLocation:
        room = listLocation[sensor][4]
        if i == 0:
            response = "The mac address " + listLocation[sensor][2] + " is in the " + room
        elif i > 0:
            response = response + ", near the " + room + " (" + str(listLocation[sensor][3]) + " db)"
        i = i + 1
    return response


# Insert vector in vector_location.csv
# Format example in csv file: Salon;{'test2': -60, 'test8': -80}
def insertVectorInVectorLocation(room, logs):
    vectorLocationModel = vlm.VectorLocationModel()
    vectorIDToAdd = room
    vectorContentToAdd = {}
    sensorConfigFile = scm.SensorConfigModel()
    listNameSensor = sensorConfigFile.content['Name'].values.tolist()
    for log in logs:
        for name in listNameSensor:
            if name in str(log[0]).lower():
                vectorContentToAdd[name] = log[3]
    vectorLocationModel.insertValue(vectorIDToAdd, str(vectorContentToAdd))
    test = vectorLocationModel.getVectorsForRoom("Salon")


# Get list of the vectors corresponding to the one  given
def compareEuclideanDistanceVector(vectorToCompare):
    vectorLocationModel = vlm.VectorLocationModel()
    dictionaryVectors = vectorLocationModel.getContentDictionaryFormat()
    print("################## Dictionary vector ##################")
    print(dictionaryVectors[0]["Room"])
    print(dictionaryVectors[0]["Content"])
    print(dictionaryVectors[0]["Content"]["test2"])


# Run RSSI Manager
def run(macAddress, DateLog):
    # List logs with the same mac address in 15 seconds range
    listOfLogsInTheGoodTimeRange = sortLogsInTheGoodTimeRange(macAddress, DateLog, False)
    print("################## List in the good time range ##################")
    print(listOfLogsInTheGoodTimeRange)
    if len(listOfLogsInTheGoodTimeRange) == 0:
        return None
    print("################## List of logs cleaned (without duplicate and with good room name ##################")
    listOfLogsCleaned = deleteDuplicateLogAndGetRoomName(listOfLogsInTheGoodTimeRange)
    print(listOfLogsCleaned)
    compareEuclideanDistanceVector(listOfLogsCleaned)
    # Keep only logs that are in the good RSSI range (configured in sensor side)
    # listLogsInTheGoodRssiRange = sortLogsInTheGoodRssiRange(listOfLogsInTheGoodTimeRange)
    # if len(listLogsInTheGoodRssiRange) == 0:
    #     return None
    # Calculate euclidean distance
    # listDistance = calculateEuclideanDistance(listLogsInTheGoodRssiRange)
    # Use euclidean distance to determine an approximate location
    # listLocation = determineLocation(listDistance, DateLog)
    # Format the approximate location to human language
    # response = displayLocation(listLocation)
    # return response


# def test():
#     listOfLogsInTheGoodTimeRange = sortLogsInTheGoodTimeRange("A1:B5:R1:N1:B9", "2020-10-11T21:38:44Z")
#     listLogsInTheGoodRssiRange = sortLogsInTheGoodRssiRange(listOfLogsInTheGoodTimeRange)
#     listDistance = calculateEuclideanDistance(listLogsInTheGoodRssiRange)
#     listLocation = determineLocation(listDistance, "2020-10-11T21:38:44Z")
#     response = displayLocation(listLocation)
#     return response


# if __name__ == "__main__":
#     # execute only if run as a script
#     test()
