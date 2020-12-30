import constant as const
import sensorLog as s
import pandas as pd

def read_csv(pathfile):
    log_file = pd.read_csv(pathfile, sep=';')

def appendInFile(dataFrame):
    dataFrame.to_csv(filepath, mode='a', sep=';')

def sortByName(pathfile, name):
    log_file = pd.read_csv(pathfile, sep=';')
    result = log_file.loc[log_file['Name'] == name]

def sortByDate(pathfile, date):
    log_file = pd.read_csv(pathfile, sep=';')
    result = log_file.loc[log_file['Date'] == date]

def sortByBluetoothMacAddress(pathfile, bluetoothAdress):
    log_file = pd.read_csv(pathfile, sep=';')
    result = log_file.loc[log_file['Mac address'] == bluetoothAdress]

#read_csv(const.TEST_BLUETOOTH_PATH)
sortByName(const.TEST_BLUETOOTH_PATH, 'Wylie Chapman')
sortByDate(const.TEST_BLUETOOTH_PATH, '2020-11-02T08:55:33-08:00')
sortByBluetoothMacAddress(const.TEST_BLUETOOTH_PATH, 'A9:B5:G7:E5:L1')