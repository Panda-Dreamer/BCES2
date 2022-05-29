import os
import json
import bottle
import argparse
from datetime import datetime, date
import traceback
import tempfile
import asyncio            
import time
from multiprocessing import freeze_support
import gevent
import config as cfg
import analyze
from tasks import analyse 
import uuid

def clearErrorLog():
    
    if os.path.isfile(cfg.ERROR_LOG_FILE):
        os.remove(cfg.ERROR_LOG_FILE)





@bottle.route('/healthcheck', method='GET')
def healthcheck():
    data = {'msg': 'Server is healthy.'}
    return json.dumps(data)

@bottle.route('/analyze', method='POST')
def handleRequest():
    upload = bottle.request.files.get('audio')
    thread_uuid = str(uuid.uuid4())
    path = "./transfer/{}.{}".format(thread_uuid+"-sound", upload.filename.split('.')[1])
    resultpath = "./transfer/{}".format(thread_uuid+"-result")
    upload.save(path)
    print(upload)
    mdata = json.loads(bottle.request.forms.get('meta'))
    result = analyse.delay(mdata,path,resultpath)

    while result.ready() == False:
        gevent.sleep(0.01)
    return result.get()
    

if __name__ == '__main__':

    # Freeze support for excecutable
    freeze_support()

    # Clear error log
    clearErrorLog()

    # Parse arguments
    parser = argparse.ArgumentParser(description='API endpoint server to analyze files remotely.')
    parser.add_argument('--host', default='0.0.0.0', help='Host name or IP address of API endpoint server. Defaults to \'0.0.0.0\'')   
    parser.add_argument('--port', type=int, default=8080, help='Port of API endpoint server. Defaults to 8080.')   
    parser.add_argument('--spath', default='uploads/', help='Path to folder where uploaded files should be stored. Defaults to \'/uploads\'.')
    parser.add_argument('--threads', type=int, default=4, help='Number of CPU threads for analysis. Defaults to 4.')
    parser.add_argument('--locale', default='en', help='Locale for translated species common names. Values in [\'af\', \'de\', \'it\', ...] Defaults to \'en\'.')

    args = parser.parse_args()

   # Load eBird codes, labels
    cfg.CODES = analyze.loadCodes()
    cfg.LABELS = analyze.loadLabels(cfg.LABELS_FILE)

    # Load translated labels
    lfile = os.path.join(cfg.TRANSLATED_LABELS_PATH, os.path.basename(cfg.LABELS_FILE).replace('.txt', '_{}.txt'.format(args.locale)))
    if not args.locale in ['en'] and os.path.isfile(lfile):
        cfg.TRANSLATED_LABELS = analyze.loadLabels(lfile)
    else:
        cfg.TRANSLATED_LABELS = cfg.LABELS  

    # Set storage file path
    cfg.FILE_STORAGE_PATH = args.spath

    # Set min_conf to 0.0, because we want all results
    cfg.MIN_CONFIDENCE = 0.0

    output_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
    output_file.close()

    # Set path for temporary result file
    cfg.OUTPUT_PATH = output_file.name

    # Set result type
    cfg.RESULT_TYPE = 'audacity'

    # Set number of TFLite threads
    cfg.TFLITE_THREADS = max(1, int(args.threads))

    # Run server
    print('UP AND RUNNING! LISTENING ON {}:{}'.format(args.host, args.port), flush=True)
    try:
        bottle.run(host=args.host, port=args.port, quiet=True)
    finally:
        os.unlink(output_file.name)
