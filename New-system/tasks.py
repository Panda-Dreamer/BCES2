from celery import Celery
import analyze

app = app = Celery('tasks', backend='rpc://', broker='pyamqp://')

def makeConfig(debug):
    settings = {
        'LATITUDE':-1,
        'LATITUDE' : -1,
        'LONGITUDE' : -1,
        'WEEK' : -1,
        'SIGMOID_SENSITIVITY' : 1.0,
        'LOCATION_FILTER_THRESHOLD' : 0.03,
        'LABELS_FILE' : './Files/Labels.txt',
        'CODES_FILE' : './Files/Codes.json',
        'SPECIES_FILE' : './Files/SpeciesList.json',
        'FR_LABELS_FILES' : './Files/Labels_FR.txt',
        'Debug': debug,
        'SAMPLE_RATE':48000,
        'SIG_LENGTH':3.0,
        'SIG_MINLEN':3.0,
        'LABELS':[],
        'CODES':[],
        'FR_LABELS':{}
    }



    return settings



@app.task
def analyse(audio_path, debug):
    config = makeConfig(debug)
    results = analyze.analyzeFile(audio_path, config)
    if results.status==True:
        return results
    else:
        return results


