import flask
from flask import request

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>ADS API</h1><p>Welcome to ADS API, here you can find and manage all sensors logs registered.</p>"


@app.route('/allDataDay', methods=['GET'])
def allDataDay():
        # Check if an ID was provided as part of the URL.
        # If ID is provided, assign it to a variable.
        # If no ID is provided, display an error in the browser.
        if 'id' in request.args:
            id = int(request.args['id'])
        else:
            return "Error: No id field provided. Please specify an id."
        pathFile = const.ARCHIVE_LOG_PATH + id + '/all_logs.csv'
        logFileModel = slfm.SensorLogFileModel(pathFile)
        return logFileModel.content


def run():
    app.run()