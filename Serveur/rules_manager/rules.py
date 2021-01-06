from Serveur.sensor_manager import SensorLogFileModel as slfm


# TODO
# Return true if this is a priority
def isAPriority(pathFile):
    logSensor = slfm.SensorLogFileModel(pathFile)


def run(pathFile):
    isAPriority(pathFile)

