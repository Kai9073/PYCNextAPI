from flask import Flask, request, Response, send_file
from flask_cors import CORS

from PycSession import Pypyc as PycSession
from PycSession import CredentialsError

from pycnetParser import pycnet
from pycnetTypes import baseUrl, CredsExpiredException

import logging
import json
import traceback
import io

logging.getLogger('werkzeug').disabled = True

app = Flask('app')
CORS(app)


@app.route('/creds/<pyccode>')
def getCredentislas(pyccode):
    pyc = PycSession()
    try:
        creds = pyc.getCreds(pyccode, request.args.get('pass'))
        return creds
    except CredentialsError:
        return Response("{'message':'Invalid password'}",
                        status=401,
                        mimetype='application/json')



@app.route('/messages/<page>', methods=['GET'])
def getMessages(page=1):
    if request.method == 'GET':
        try:
            sessid = request.headers.get('PYC-PHPSESSID')
            token = request.headers.get('PYC-TOKEN')
            if sessid is None or token is None:
                return Response("{'message':'invalid headers'}",
                                status=400,
                                mimetype='application/json')
            messages = pycnet.getMessages(
                {
                    'PHPSESSID': sessid,
                    'access_token': token
                }, {'page': page})
            messages_dict = list(map(lambda msg: msg.dict, messages))
            return Response(bytes(json.dumps(messages_dict),
                                  'ascii').decode('unicode-escape'),
                            status=200,
                            mimetype='application/json')
        except CredsExpiredException:
            return Response("{'message':'Refresh credentials'}",
                            status=401,
                            mimetype='application/json')
        except Exception as e:
            print(e, traceback.format_exc())
            return Response(str(e), status=500)



@app.route('/message/<_id>', methods=['GET', 'DELETE'])
def getMessage(_id):
    if request.method == 'GET':
        try:
            sessid = request.headers.get('PYC-PHPSESSID')
            token = request.headers.get('PYC-TOKEN')
            if sessid is None or token is None:
                return Response("{'message':'invalid headers'}",
                                status=400,
                                mimetype='application/json')
            message = pycnet.getMessage(
                {
                    'PHPSESSID': sessid,
                    'access_token': token
                }, {'id': _id})
            return Response(json.dumps(message), status=200, mimetype='application/json')
        except CredsExpiredException:
            return Response("{'message':'Refresh credentials'}",
                            status=401,
                            mimetype='application/json')
        except Exception as e:
            print(e, traceback.format_exc())
            return Response(str(e), status=500)
    if request.method == 'DELETE':
        pass



@app.route('/image', methods=['GET'])
def getImage():
    sessid = request.args.get('s')
    token = request.args.get('t')
    dir = request.args.get('dir')
    item = request.args.get('item')
    try:
        image_bytes = pycnet.getImage(
            {
                'PHPSESSID': sessid,
                'access_token': token
            }, {
                'dir': dir,
                'item': item
            })
        extension = item.split('.')[-1]
        return send_file(
            image_bytes,
            mimetype='image/jpeg' if extension == 'jpg' else extension,
            as_attachment=True,
            download_name=item)
    except CredsExpiredException:
        return Response("{'message':'Refresh credentials'}",
                        status=401,
                        mimetype='application/json')
    except Exception as e:
        print(e, traceback.format_exc())
        return Response(str(e), status=500)



app.run(host='0.0.0.0', port=8080)
