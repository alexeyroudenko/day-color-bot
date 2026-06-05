import glob
import urllib
from urllib.parse import quote  
from flask import jsonify
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, disconnect
import pickle
from flask import request, jsonify

app = Flask(__name__, 
    static_url_path='/data', 
    static_folder='../data', 
    template_folder='templates'
)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

socketio = SocketIO(app, async_mode="threading") 

from redis import Redis
redis = Redis(host='redis', port=6379)

import logging
app.logger.disabled = True
log = logging.getLogger('werkzeug')


  
  
'''

    API
''' 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/spot/')
def spot():
    import os
    img_path = f"/data/trends/202[0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9].jpg"
    spotes = glob.glob(img_path)
    spotes.sort(key=os.path.getctime) 
    spot_path = [spotes[len(spotes)-1]]
    response = jsonify(spot_path)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    return response

@app.route('/spots/')
def spots():
    import os
    print(os.getcwd())
    rimages = []
    for img in glob.glob("/data/trends/202[0-9]-[0-9][0-9]-[0-9][0-9]-[0-9][0-9].jpg"):
        filename = img.replace("#","%23")
        tag = str(img).split("/")[2]
        tag = str(tag)[:-4]
        rimages.append({"filename":filename, "tag":tag}) #quote
    return jsonify(rimages)

@app.route('/words/')
def words():
    import os
    print(os.getcwd())
    rimages = []
    idd = 0
    for img in glob.glob("/data/words/*.jpg"):
        filename = img.replace("#","%23")
        tag = str(img).split("/")[3]
        tag = str(tag)[:-4]
        if not "_blr" in filename and not "_src" in filename and not "_pal" in filename and not "_som" in filename:
            idd+=1
            rimages.append({"id":idd, 
                            "filename":filename, 
                            "filename_src":f"/data/words/{tag}_src.jpg", 
                            "filename_som":f"/data/words/{tag}_som.jpg", 
                            "filename_pal":f"/data/words/{tag}_pal.jpg", 
                            "tag":tag
                            }) #quote
        
    # rimages = rimages[0:20]  
    response = jsonify(rimages)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    return response


@app.route('/semantic/')
def semantic():
    
    import random
    

    import json
    with open('/data/###/words.json', 'r', encoding='utf-8') as f:        
        d=json.load(f)        
        random.shuffle(d)
    
    response = jsonify(d)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    return response

@app.route('/word/<word_action>/<word>/') 
def word_action(word_action, word):
    print(word_action, word)
    with open("/tmp/word.txt", "w") as file:
        file.write(f"{word}")

    username = "airflow"
    password = "airflow"
    import requests
    import base64
    userpass = username + ':' + password
    encoded_userpass = base64.b64encode(userpass.encode()).decode()
    AIRFLOW_URL = 'http://airflow-webserver:8080/api/v1/dags/receive_word/dagRuns'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Basic {encoded_userpass}"
    }
    data = {
        "conf": {"word_action":word_action, "word":word}  # Вы можете передать конфигурацию, если это необходимо
    }
    response = requests.post(AIRFLOW_URL, headers=headers, json=data)
    # print(response.json())

    return response.json()

@app.route('/trends/')
def trends():
    tags = []
    out_folder = "/data/###/"
    out_data_path = f"{out_folder}trends.txt"    
    with open(out_data_path, 'r') as f:
        tagsf = f.readlines()    
        for tag in tagsf:
            tag_obj = {}
            tag_obj['tag'] = tag.strip()
            import random
            tag_obj['count'] = random.randint(0,128)
            tags.append(tag_obj)
            
    response = jsonify(tags)        
    response.headers.add("Access-Control-Allow-Origin", "*")            
    return response

'''

    Called from container
''' 
@app.route('/spot/new/', methods=['GET', 'POST'])
def new_spot():
    import os
    print(os.getcwd())                    
    socketio.emit('spot', [request.form])        
    return "spot"


@app.route('/img/new/', methods=['GET', 'POST']) 
def new_img():
    if request.method == 'POST':    
        path = request.form.get('path')
        tag = request.form.get('tag')    
        path = path[4:]
        path = path.replace("#","%23")
         
    import os
    print(os.getcwd())        
        
    print(f'new_img path: {path} for tag: {tag}')   
    socketio.emit('img', ["new", path, tag])        
    return "hello"



'''

    Websocket
''' 
@socketio.on('connect')
def handle_connect(message):
    print('connect message')

@socketio.on('update')
def handle_update(message):
    data = message['data']
    print('update message: ' + str(data))
    
@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)    
    redis.incr('hits')
 
@socketio.event
def my_ping():
    emit('my_pong')
    
def event_trends_handler(msg):
    print(f"flask event_trends_handler {msg}")
    emit('tags', msg)
  
  
  
'''

    App
'''  
if __name__ == '__main__':
    print("start flask 1.1.0") 
    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True, debug=True)