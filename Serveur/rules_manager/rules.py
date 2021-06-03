from Serveur.sensor_manager import SensorLogFileModel as slfm
from Serveur.rules_manager import SensorConfigModel as scm
from Serveur.rules_manager.list import listModel as lm
from Serveur.message import SendSMSModel


# Return the priority value
# Priority order :
# 1 => Vault
# 2 => Strict
# 3 => Busy place
# 4 => Open bar
def getPriority(pathFile):
    logConfigSensor = scm.SensorConfigModel()
    logConfigSensor.content.set_index('Name', inplace=True)
    logSensor = slfm.SensorLogFileModel(pathFile)
    resultSearch = logConfigSensor.content.loc[logSensor.sensorName]
    return resultSearch['Priority']


# Get the location of the lines to analyze
def getLocation(pathFile):
    logConfigSensor = scm.SensorConfigModel()
    logConfigSensor.content.set_index('Name', inplace=True)
    logSensor = slfm.SensorLogFileModel(pathFile)
    resultSearch = logConfigSensor.content.loc[logSensor.sensorName]
    return resultSearch['Room_Description']


# Return true if the mac address is in the white list file
def isInWhiteList(mac_address):
    whiteListFile = lm.ListModel()
    return mac_address in whiteListFile.contentWhiteList['Mac_Address'].values


# Return true if the mac address is in the black list file
def isInBlackList(mac_address):
    blackList = lm.ListModel()
    return mac_address in blackList.contentBlackList['Mac_Address'].values


# Run vault rule
# row [0] = index
# row [1] = ID
# row [2] = Date
# row [3] = Mac_Address
# row [4] = RSSI
def runVaultRules(pathFile, linesToAnalyzed):
    logSensor = slfm.SensorLogFileModel(pathFile)
    print("Someone entered in vault " + logSensor.sensorName + ", processing...")
    for row in linesToAnalyzed.itertuples():
        date = row[2]
        macAddress = row[3]
        rssi = row[4]
        if isInBlackList(macAddress):
            sendAlert("Black listed mac address " + macAddress + " is in vault " + logSensor.sensorName + " - date : " + date)
            print("Black listed mac address !")
        elif isInWhiteList(macAddress):
            print("Access authorized for mac address : " + macAddress)
            continue
        else:
            print("Mac address not known ! ")
            sendAlert("Mac address not known : " + macAddress + " is in vault " + logSensor.sensorName + " - date : " + date)


def runStrictRules(pathFile, linesToAnalyzed):
    logSensor = slfm.SensorLogFileModel(pathFile)
    print("Someone entered in strict sensor " + logSensor.sensorName + ", processing...")
    for row in linesToAnalyzed.itertuples():
        date = row[2]
        macAddress = row[3]
        if isInBlackList(macAddress):
            print("Black listed mac address : " + macAddress + " !")
            sendAlert("Black listed mac address " + macAddress + " is in strict sensor " + logSensor.sensorName + " - date : " + date)
        elif isInWhiteList(macAddress):
            print("Access authorized for mac address : " + macAddress)
            continue
        else:
            print("Mac address not known : " + macAddress + " is in strict sensor " + logSensor.sensorName + " - date : " + date)


# Send an alert to the mobile of the user
def sendAlert(content):
    sendSms = SendSMSModel.SendSMSModel()
    sendSms.sendMessage(content)


# TODO : get a better management rules
# run the rule manager
def run(pathFile, linesToAnalyzed):
    # 1 => Check if the file received is a priority
    priority = getPriority(pathFile)
    # 2 -> Check the location
    location = getLocation(pathFile)
    print(location)
    if priority == 1:
        runVaultRules(pathFile, linesToAnalyzed)
    elif priority == 2:
        runStrictRules(pathFile, linesToAnalyzed)
    elif priority == 3:
        print("Priority 3")
    elif priority == 4:
        print("Open bar, nothing to do ;)")
        ...
    else:
        print("Out of scope priority")
