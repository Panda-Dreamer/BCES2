from celery import Celery
import analyze

app = app = Celery('tasks', backend='rpc://', broker='pyamqp://')

def makeConfig(debug):
    settings = {}
    settings.LATITUDE = -1
    settings.LONGITUDE = -1
    settings.WEEK = -1
    settings.SIGMOID_SENSITIVITY = 1.0
    settings.LOCATION_FILTER_THRESHOLD = 0.03
    settings.LABELS_FILE = './Files/Labels.txt'
    settings.CODES_FILE = './Files/Codes.json'
    settings.SPECIES_FILE = './Files/SpeciesList.json'
    settings.FR_LABELS_FILES = './Files/Labels_FR.txt'
    settings.Debug = debug

    #Sound settings

    settings.SAMPLE_RATE = 48000
    settings.SIG_LENGTH = 3.0
    settings.SIG_MINLEN = 3.0



    return settings



@app.task
def analyse(audio_path, debug):
    config = makeConfig(debug)
    results = analyze.analyzeFile(audio_path, config)
    if results.status==True:
        return results
    else:
        return results


@app.task
def server_homepage():
    