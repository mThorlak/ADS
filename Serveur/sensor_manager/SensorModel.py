import pandas

from Serveur.sensor_manager import SensorContentModel, RECEPTION_LOG_PATH


class SensorModel:
    Sensor_Name = ""
    Date_Sensor = ""
    Content = [SensorContentModel]

    def __init__(self, sensor_name, date_sensor, content):
        self.Sensor_Name = sensor_name
        self.Date_Sensor = date_sensor
        self.Content = content

    def getSensorDescription(self):
        return "{ Sensor name : " + self.Sensor_Name + "; sensor date : " + self.Date_Sensor + "; }"

    def getContent(self):
        return self.Content

    def getSensorName(self):
        return self.Sensor_Name

    def getSensorDate(self):
        return self.Date_Sensor

    def convertIntoCsvLogFile(self):
        open(RECEPTION_LOG_PATH + '/' + self.Sensor_Name + '__' + self.Date_Sensor + '.csv', "x")
        Content_To_Dataframe = pandas.DataFrame(self.getContent())
        Content_To_Dataframe.to_csv(RECEPTION_LOG_PATH + '/' + self.Sensor_Name + '__' + self.Date_Sensor + '.csv', index=False)