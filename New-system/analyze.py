import json
import datetime
import audio
import model
import numpy as np
import operator




def loadCodes(code_files):

    with open(code_files, 'r') as cfile:
        codes = json.load(cfile)

    return codes

def loadLabels(labels_file):

    labels = []
    with open(labels_file, 'r') as lfile:
        for line in lfile.readlines():
            text = line.replace('\n', '')
            labels.append(text)    
    return labels

def loadFRLabels(FRlabels_file):
    
    FRlabels = {}
    with open(FRlabels_file, 'r') as lfile:
        for line in lfile.readlines():
            text = line.replace('\n', '')
            FRlabels[text.split("_")[0]] = text
    return FRlabels






def debugLog(info,msg,status):
    if(status == True):
        print('{} -- {}'.format(info,msg))

def getRawAudioFromFile(path,config):
    
    # Open file
    sig, rate = audio.openAudioFile(path, config.SAMPLE_RATE)

    # Split into raw audio chunks
    chunks = audio.splitSignal(sig, rate, config.SIG_LENGTH, config.SIG_OVERLAP, config.SIG_MINLEN)

    return chunks

def predict(samples, config):

    data = np.array(samples, dtype='float32')
    prediction = model.predict(data)
    prediction = model.flat_sigmoid(np.array(prediction), sensitivity=-config.SIGMOID_SENSITIVITY)

    return prediction

def format(results, config):
    id = 0
    formatted_results = []
    for timestamp in sorted(results, key=lambda t: float(t.split('-')[0])):
        for index in results[timestamp]:
            if index[1] > 0.1 and index[0] in config.CODES:
                label = config.LABELS.index(index[0])
                data = {
                    'id': id,
                    'label': label,
                    'start': float(timestamp.split('-')[0]),
                    'end': float(timestamp.split('-')[1]),
                    'specie_code': config.CODES[index[0]],
                    'specie_name': label.split("_")[1],
                    'confidence': index[1],
                    'FR_label': config.FR_LABELS[label.split("_")[0]]
                }
                formatted_results.append(data)
                id=id+1

    return formatted_results


def analyzeFile(audio_path, config):
    print(config)
    start_time = datetime.datetime.now()
    debugLog("analyzeFile", "Starting for file: "+str(audio_path), config.Debug)
    config.LABELS = loadLabels(config.LABELS_FILE)
    config.CODES = loadCodes(config.CODES_FILE)
    config.FR_LABELS = loadFRLabels(config.FR_LABELS_FILE)

    chunks = getRawAudioFromFile(audio_path,config)

    if(len(chunks) <= 0): #No audio chunks found
        debugLog("analyzeFile", "No chunks found", config.Debug)
        return {'status':False,'message':'No chunks found'}
    
    try:
        start = 0
        length = config.SIG_LENGTH
        end = start+length
        results = {}
        samples = []
        timestamps = []

        for index in range(len(chunks)):
             samples.append(chunks[index])
             timestamps.append([start, end])

             start += length
             end = start + length

             if index < len(chunks) - 1 and len(samples) < config.BATCH_SIZE:
                    continue

             p = predict(samples, config)

             for i in range(len(samples)):
                  s_start, s_end = timestamps[i]
                  pred = p[i]
                  p_labels = dict(zip(config.LABELS, pred))
                  p_sorted =  sorted(p_labels.items(), key=operator.itemgetter(1), reverse=True)
                  results[str(s_start) + '-' + str(s_end)] = p_sorted
             samples = []
             timestamps = []
        

        #Format results
        fresults =  format(results, config)

        debugLog("analyzeFile", "Finished for file: "+str(audio_path), config.Debug)
        return {'status':True,'message':'Success','results':fresults, 'time':(datetime.datetime.now() - start_time).total_seconds()}


    except:
        debugLog("analyzeFile", "Error while analysing chunk", config.Debug)
        return {'status':False,'message':'Error while analysing chunk'}