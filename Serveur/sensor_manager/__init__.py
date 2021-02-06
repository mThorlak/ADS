from pathlib import Path

ACTUAL_DIRECTORY = Path(__file__).parent.absolute().as_posix()
ARCHIVE_LOG_PATH = Path(__file__).parent.absolute().as_posix() + '/archiv_log/'
RECEPTION_LOG_PATH = Path(__file__).parent.absolute().as_posix() + '/reception_log/'
BUFFER_FILE_PATH = Path(__file__).parent.absolute().as_posix() + '/buffer_sensors.csv'
