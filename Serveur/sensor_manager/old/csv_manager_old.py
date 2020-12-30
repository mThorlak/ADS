import csv

#Read all csv file
def readCsvFile(pathfile):
    with open(pathfile, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            print(', '.join(row))
            
#Convert csv file into Sensor object
def castLogIntoSensorLog(pathfile):
    listSensorLog = []
    sensorLog = s.SensorLog();
    with open(pathfile, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            i = 0
            for column in row :
                if i == 0 :
                    print ('ok')
                    print(column)
                i = i + 1
        listSensorLog.append(sensorLog)
        sensorLog = s.SensorLog();
    return listSensorLog
    
#readCsvFile('/home/pi/Documents/Smartphone_Detector_Project/log_files/test.csv')
#listSensorLog = castLogIntoSensorLog('/home/pi/Documents/Smartphone_Detector_Project/log_files/test.csv')
