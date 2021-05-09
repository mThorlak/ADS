class SensorContentModel:
    ID = ""
    Date = ""
    Mac_Address = ""
    RSSI = ""

    # Content -> dataFrame coming from the log file
    content = ""

    def __init__(self, content_array):
        self.ID = content_array["ID"]
        self.Date = content_array["Date"]
        self.Mac_Address = content_array["Mac_Address"]
        self.RSSI = content_array["RSSI"]

    def getContentInformation(self):
        return "{ ID : " + self.ID + "; Date : " + self.Date + \
               ";  Mac_Address : " + self.Mac_Address + ";  RSSI : " + self.RSSI + "}"

    def getContent(self):
        return self.content

    def getID(self):
        return self.ID

    def getDate(self):
        return self.Date

    def getMac_Address(self):
        return self.Mac_Address

    def getRSSI(self):
        return self.RSSI
