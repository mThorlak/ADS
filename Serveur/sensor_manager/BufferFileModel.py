import pandas as pd
from Serveur.sensor_manager import BUFFER_FILE_PATH


class BufferFileModel:
    pathFile = ""

    # Content -> dataFrame coming from the log file
    content = ""

    def __init__(self):
        self.pathFile = BUFFER_FILE_PATH
        self.content = pd.read_csv(self.pathFile)

