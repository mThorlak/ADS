from datetime import datetime

import Serveur.api.service as service
from Serveur.sensor_manager import SensorLogFileModel as slfm, ARCHIVE_LOG_PATH
from Serveur.rules_manager import SensorConfigModel as scm
from Serveur.sensor_manager import SensorAllLogsFileModel as salfm
import Serveur.rules_manager.rules as rules


# Get RSSI range of a specified config sensor
def getRssiRange(pathFile):
    logConfigSensor = scm.SensorConfigModel()
    logConfigSensor.content.set_index('Name', inplace=True)
    logSensor = slfm.SensorLogFileModel(pathFile)
    resultSearch = logConfigSensor.content.loc[logSensor.sensorName]
    return resultSearch['Min_Range', 'Max_Range']


# Sort that received signal from the specified mac_address during the last or next 30 seconds
def sortLogsInTheGoodTimeRange(macAddress, date):
    date = date[:-1]
    dateConverter = datetime.strptime(date, '%Y-%d-%mT%H:%M:%S')
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
    # Check all the times and get the ones which are in the last 30 seconds
    i = 0
    storeIndex = []
    while i < len(dateLogs):
        dateConverted = datetime.strptime(dateLogs[i], '%Y-%d-%mT%H:%M:%S')
        if dateConverted.time() < dateConverter.time():
            timeSubtracted = (dateConverter - dateConverted).seconds
        else:
            timeSubtracted = (dateConverted - dateConverter).seconds
        # Collect only the logs similar in a 30 seconds range
        if timeSubtracted <= 30:
            storeIndex.append(i)
        i = i + 1
    result = []
    for i in storeIndex:
        result.append(allTodayLogsMacAddressList[i])
    return result


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


# TODO : to finish
# {'Test3-01': ['Test3-01', '2020-13-10T21:38:20Z', 'A1:B5:R1:N1:B9', 1, 'Garage'],
# 'Test8-02': ['Test8-02', '2020-13-10T21:39:10Z', 'A1:B5:R1:N1:B9', 59, 'Cuisine'],
# 'Test4-05': ['Test4-05', '2020-13-10T21:39:03Z', 'A1:B5:R1:N1:B9', 49, 'Salon']}
def determineLocation(listDistance, date):
    print(listDistance)
    # Get the good all logs file
    date = date[:-1]
    dateConverter = datetime.strptime(date, '%Y-%d-%mT%H:%M:%S')
    dateOfTheDay = dateConverter.date().strftime("%d-%m-%Y")
    pathFile = ARCHIVE_LOG_PATH + dateOfTheDay + '/all_logs.csv'
    allLogsFileModel = salfm.SensorAllLogsFileModel(pathFile)
    print(allLogsFileModel.content)
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
    print(result)
    print(sensorConfigModel.content["Name"].values)
    return None


# TODO : sort list of logs sorted with the good range

def test():
    listOfLogsSorted = sortLogsInTheGoodTimeRange("A1:B5:R1:N1:B9", "2020-10-11T21:38:44Z")
    listDistance = calculateEuclideanDistance(listOfLogsSorted)
    determineLocation(listDistance, "2020-10-11T21:38:44Z")
    return None


if __name__ == "__main__":
    # execute only if run as a script
    test()



