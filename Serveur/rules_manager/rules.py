from Serveur.sensor_manager import SensorLogFileModel as slfm
from Serveur.rules_manager import SensorConfigModel as scm
from Serveur.rules_manager.list import listModel as lm


# Priority order :
# 1 => Coffre fort
# 2 => Stricte
# 3 => Lieu animé
# 4 => Open bar

# Return true if the file is a priority
def isAPriority(pathFile):
    logConfigSensor = scm.SensorConfigModel()
    logSensor = slfm.SensorLogFileModel(pathFile)
    resultSearch = logConfigSensor.content.loc[logSensor.sensorName]
    return resultSearch['Priority'] == 1


# Return true if the mac address is in the white list file
def isInWhiteList(mac_address):
    whiteListFile = lm.ListModel()
    return mac_address in whiteListFile.contentWhiteList['Mac_Address'].values


# Return true if the mac address is in the black list file
def isInBlackList(mac_address):
    blackList = lm.ListModel()
    return mac_address in blackList.contentBlackList['Mac_Address'].values


# TODO
    # 0 => make a buffer of all the new lines to read
    # 1 => check if the new logs are a priority
    # 2 => chek if the mac_adress is in whiteList or blackList


# TODO
# Send an alert to the mobile of the user
def sendAlert():
    print("Alert sent")


def run(pathFile):
    if isAPriority(pathFile):
        sendAlert()
    print(isInWhiteList('Test1'))
    print(isInBlackList('Test2'))
