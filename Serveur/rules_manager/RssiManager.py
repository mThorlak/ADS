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


# Get all sensors with room description and range that received signal from the specified mac_address at the same time
def calculateEuclideanDistance(listOfLogsSorted):
    # => Récupérer les logs qui sont à la même minute, à quelques secondes prêt
    # Comparer la puissance du RSSI qu'ils ont récupérés
    # Distance euclidienne, avec le plus fort RSS pour valeur 1
    return None


# Get all sensors with room description and range that received signal from the specified mac_address at the same time
# def function...

def test():
    listOfLogsSorted = sortLogsInTheGoodTimeRange("A1:B5:R1:N1:B9", "2020-10-11T21:38:44Z")
    # calculateEuclideanDistance(listOfLogsSorted)
    return None


if __name__ == "__main__":
    # execute only if run as a script
    test()



