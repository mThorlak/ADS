class SensorLog:

    bluetoothMacAddress = None
    dateTime = None

    def __init__(self):
        bluetoothMacAddress = None
        dateTime = None

    def __str__(self):
        return self.bluetoothMacAddress + " - " + self.dateTime;

    def setBluetoothMacAddress(self, BluetoothMacAdress):
        self.bluetoothMacAddress = BluetoothMacAdress

    def setDateTime(self, DateTime):
        self.dateTime = DateTime