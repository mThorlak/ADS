import pandas as pd
from Serveur.rules_manager import WHITE_LIST_PATH, BLACK_LIST_PATH


class ListModel:
    whiteListPathFile = ""
    blackListPathFile = ""

    # Content -> dataFrame coming from the log file
    contentWhiteList = ""
    contentBlackList = ""

    def __init__(self):
        self.whiteListPathFile = WHITE_LIST_PATH
        self.blackListPathFile = BLACK_LIST_PATH
        self.contentWhiteList = pd.read_csv(self.whiteListPathFile)
        self.contentBlackList = pd.read_csv(self.blackListPathFile)
