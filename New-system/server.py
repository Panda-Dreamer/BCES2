import os
import json
import bottle
import argparse
import uuid
import gevent

from tasks import analyse 

@bottle.route('/healthcheck', method='GET')
def healthcheck():
    data = {'msg': 'Server is healthy.'}
    return json.dumps(data)

@bottle.route('/static/<filename>', method='GET')
def server_static(filename):
    return bottle.static_file(filename, root='./Files/website')


@bottle.route('/', method='GET')
def home():
    return bottle.static_file("index.html", root='./Files/website')


@bottle.route('/analyze', method='POST')
def handleRequest():
    upload = bottle.request.files.get('audio')
    thread_uuid = str(uuid.uuid4())
    path = "./transfer/{}.{}".format(thread_uuid+"-sound", upload.filename.split('.')[1])
    upload.save(path)
    print(upload)
    result = analyse.delay(path, args.debug)

    while result.ready() == False:
        gevent.sleep(0.01)
    # Delete file
    try:
        os.remove(path)
    except:
        pass
    return result.get()
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='API endpoint server to analyze files remotely.')
    parser.add_argument('--host', default='0.0.0.0', help='Host name or IP address of API endpoint server. Defaults to \'0.0.0.0\'')   
    parser.add_argument('--port', type=int, default=3000, help='Port of API endpoint server.')   
    parser.add_argument('--debug', type=bool, default=False, help='Enable debug mode.')

    args = parser.parse_args()

    # Load translated labels
    print('UP AND RUNNING! LISTENING ON {}:{}'.format(args.host, args.port), flush=True)
    bottle.run(host=args.host, port=args.port, quiet=True)