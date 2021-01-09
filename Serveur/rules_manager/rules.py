from Serveur.sensor_manager import SensorLogFileModel as slfm
from Serveur.rules_manager import SensorConfigModel as scm


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


# TODO
# Send an alert to the mobile of the user
def sendAlert():
    print("Alert sent")


def run(pathFile):
    if isAPriority(pathFile):
        sendAlert()

