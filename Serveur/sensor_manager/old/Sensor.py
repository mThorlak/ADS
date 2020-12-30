class Sensor:

    name = None
    priority = None
    day = None

    #List of sensor log
    sensorLogsList = None

    def __init__(self, name, priority, day):
        self.name = name
        self.priority = priority
        self.day = day


    def __str__(self):
        return self.name + " - " + self.priority + " - " + self.day;