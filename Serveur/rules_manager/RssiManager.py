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


# Get all sensors with room description and range that received signal from the specified mac_address at the same time
def establishLocation(macAddress, date):
    date = date[:-1]
    dateConverter = datetime.strptime(date, '%Y-%d-%mT%H:%M:%S')
    date = dateConverter.date().strftime("%d-%m-%Y")
    allTodayLogsMacAddress = service.getLogsByDateAndMacAddress(date, macAddress)
    return allTodayLogsMacAddress
    # => Récupérer les logs qui sont à la même minute, à quelques secondes prêt
    # Comparer la puissance du RSSI qu'ils ont récupérés
        # => Déterminer le plus puissant
        # => Déterminer ceux dont le RSSI est dans la range du sensor
        # Cas 1 : le RSSI est valide pour un seul endroit => il est donc dans la piece correspondante
        # Cas 2 : le RSSI est valide pour plusieurs endroits => on dit que le user se trouve dans la piece au meilleur RSSI, en disant que c'est aussi proche des autres
        # Cas 3 : il n'est dans aucune des range => on fait rien


def test():
    test1 = establishLocation("A1:B5:R1:N1:B9", "2020-10-11T21:38:44Z")
    print(test1)
    return None


if __name__ == "__main__":
    # execute only if run as a script
    test()



