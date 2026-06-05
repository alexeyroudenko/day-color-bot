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
    static_folder='data', 
    template_folder='templates'
)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

socketio = SocketIO(app, async_mode="threading") 

# import pickle  
from redis import Redis
redis = Redis(host='redis', port=6379)
  
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help/')
def help():
    return render_template('help.html')

@app.route('/spots_page/')
def spots_page():
    return render_template('spots.html')

current_spot = None
@app.route('/ctrl/')
def ctrl():
    global current_spot
    current_spot = get_current_spot()
    return render_template('ctrl.html')

@app.route('/message/')
def message_page():
    return render_template('message.html')

@app.route('/tags')
def tags():
    try:
        trends = pickle.loads(redis.get("trends"))
    except:
        trends = ["#baystars", "#FGO", "#malatya", "たかほ", "カズラドロップ", "バーニス", "バーニス", "バーニス", "増田大輝", "バーニス"]
    # images = glob.glob("static/tags/$STORM/*")
    return jsonify(trends)

@app.route('/tags/restart')
def tags_restart():
    socketio.emit('tags_restart')
    return jsonify('tags_restart')

@app.route('/day/') 
def day_action():
    redis.incr('day')
    count = int(redis.get('day'))
    redis.publish("day", "count")
    return "sent"

@app.route('/tag/<tag>') 
def show_tag_images(tag):
    path = f"data/tags/{tag}/*"
    print(f"show_tag_images {tag} {path}")
    images = glob.glob(path)
    
    #print(images)
    rimages = []
    for img in images:
        rimages.append(img.replace("#","%23")) #quote
        
    calc_images = glob.glob("data/spot/{tag}*")
    for img in calc_images:
        rimages.append(img.replace("#","%23")) #quote
    
    out_item = {}
    
    import os
    if os.path.isfile(f"data/spot/{tag}_blr.png"):
        rimages.append(f"data/spot/{tag}_src.jpg".replace("#","%23"))
        rimages.append(f"data/spot/{tag}_pal.png".replace("#","%23"))
        rimages.append(f"data/spot/{tag}_col.png".replace("#","%23"))
        rimages.append(f"data/spot/{tag}_som.png".replace("#","%23"))
        rimages.append(f"data/spot/{tag}_blr.png".replace("#","%23"))
        
    return jsonify(rimages)


import logging
app.logger.disabled = True
log = logging.getLogger('werkzeug')
# log.disabled = True

def get_current_spot():
    import os
    img_path = f"data/spot/2024-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]_blr.png"
    spotes = glob.glob(img_path)
    spotes.sort(key=os.path.getctime) 
    spot = spotes[0]
    from PIL import Image
    image = Image.open(spot)
    current_spot = image
    return image

def rgb_to_hex(d):
    return '#{:02x}{:02x}{:02x}'.format(d[0], d[1], d[2])


@app.route('/colors/') 
def colors():
    color = redis.get("color")
    return jsonify([color])

#redis.set("color", color)

@app.route('/led/') 
def led_state():
    img = get_current_spot()   
    # pixel = img.getpixel((cx, cy))
    # color = rgb_to_hex(pixel)
    # redis.set("color", color)
    # socketio.emit('picked_color', color)
    out = []
    import random
    coords1 = (random.randint(0,500), random.randint(0,500))
    coords2 = (random.randint(0,500), random.randint(0,500))
    coords3 = (random.randint(0,500), random.randint(0,500))    
    color1 = rgb_to_hex(img.getpixel(coords1))
    color2 = rgb_to_hex(img.getpixel(coords2))
    color3 = rgb_to_hex(img.getpixel(coords3))
    color1 = rgb_to_hex((0,255,0))
    color = redis.get("color")
    # color1 = color
    colors = [color1, color2, color3]
    return jsonify([out, colors])

@app.route('/state/') 
def load_state():
    out = []
    img_path = f"data/spot/2024-[0-9][0-9]-[0-9][0-9]-[0-9][0-9]_blr.png"
    print("state", len(img_path), redis.get('state_calls'))
    if len(glob.glob(img_path)) > 0:
        import os
        import random
        spotes = glob.glob(img_path)
        spotes.sort(key=os.path.getctime) 
        spot = spotes[0]        
        from PIL import Image
        image = Image.open(spot)
        color1 = rgb_to_hex(image.getpixel((random.randint(40,100), random.randint(40,100))))
        color2 = rgb_to_hex(image.getpixel((random.randint(400,500), random.randint(200,300))))
        color3 = rgb_to_hex(image.getpixel((random.randint(40,100), random.randint(140,190))))        
        color1 = rgb_to_hex((random.randint(0,255),random.randint(0,255),random.randint(0,255)))
        colors = [color1, color2, color3]
                
        filename = spot.replace("#","%23")
        tag = str(spot).split("/")[2]
        tag = str(tag)[:-8]
        #tag = tag.encode().decode('unicode-escape')
        tag = tag.encode()
        
        mask_path = f"data/spot/{tag}*"
        for item in glob.glob(mask_path):            
            out.append("/"+item)    
            out.append("/"+spot)    
        
        # print("tag", tag)
        out.append(spot)
        # out.append(tag)
        # out.append(mask_path)
        
        redis.incr('state_calls')
        return jsonify([out, colors])
    else:
        return jsonify([])

@app.route('/state_colors/') 
def state_colors():
    txts_path = f"data/spot/2024-[0-9][0-9]-[0-9][0-9]-[0-9][0-9].txt"
    txt_patth = glob.glob(txts_path)[0]
    file = open(txt_patth, "r") 
    colors = file.read().split("\n")
    
    filename = txt_patth.replace("#","%23")
    tag = str(txt_patth).split("/")[2]
    tag = str(tag)[:-4]    
    tag = tag.encode().decode('unicode-escape')
            
    mask_path = f"data/spot/{tag}*"
    for item in glob.glob(mask_path):            
        colors.append(item)    
    colors.append(tag) 
    colors.append(mask_path)
    
    return jsonify(colors)

@app.route('/tag/<tag_action>/<tag>/') 
def tag_action(tag_action, tag):
    print(tag_action, tag)
    socketio.emit('tag', [tag_action, tag])
    return tag_action + " " + tag
    
@app.route('/tag_ctrl/<tag_action>/<tag>/') 
def tag_ctrl(tag_action, tag):
    #print(tag_action, tag)
    socketio.emit('tag', [tag_action, tag])
    redis.publish(f"{tag_action}", tag)    
    return tag
   
@app.route('/app_ctrl/<word_action>/<word>/') 
def app_ctrl(word_action, word):
        
    if word_action == "add_word":
        print("word", word_action, word)
        socketio.emit('word', [word_action, word])
        redis.publish(f"{word_action}", word)   
         
    if word_action == "switch_page":
        page = word
        socketio.emit(word_action, page)
        
    return word

@app.route('/spots')
def spots():
    import os
    print(os.getcwd())
    rimages = []
    for img in glob.glob("data/spot/*blr.png"):
        filename = img.replace("#","%23")
        tag = str(img).split("/")[2]
        tag = str(tag)[:-8]
        # tag = tag.encode().decode('unicode-escape')
        rimages.append({"filename":filename, "tag":tag}) #quote
    return jsonify(rimages)


#
# Called from container
#
@app.route('/spot/new/', methods=['GET', 'POST'])
def new_spot():
    if request.method == 'POST':
        print("#################################")
        print(request.form)
    else:         
        path = "/data/tags/増田大輝/5.jpg"    
        tag = "増田大輝"
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
        print(f"fix path {path} --------- ")
    else:         
        path = "/data/tags/増田大輝/5.jpg"    
        tag = "増田大輝"
        
    
    import os
    print(os.getcwd())        
        
    print(f'new_img path: {path} for tag: {tag}')   
    socketio.emit('img', ["new", path, tag])        
    return "hello"


@app.route('/trends')
def trends():
    outs = []    
    trends = pickle.loads(redis.get("trends"))
    for trend in trends:        
        images = glob.glob(f"static/tags/{trend}/*")
        out_item = {}
        out_item['tag'] = trend
        out_item['images'] = images
        out_item['src'] = f"static/spot/{trend}_src.jpg"
        out_item['pal'] = f"static/spot/{trend}_pal.png"
        out_item['col'] = f"static/spot/{trend}_col.png"
        out_item['som'] = f"static/spot/{trend}_som.png"
        out_item['blr'] = f"static/spot/{trend}_blr.png"
        outs.append(out_item)
    return jsonify(outs)

@socketio.on('connect')
def handle_connect(message):
    #data = message['data']з
    print('connect message')

@socketio.on('update')
def handle_update(message):
    # print('update message: ' + str(msg))
    data = message['data']
    print('update message: ' + str(data))
    
@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)    
    redis.incr('hits')
 
@socketio.event
def my_ping():
    emit('my_pong')
    
@socketio.on('mouse')
def mouse(cx, cy):
    redis.set("mx", cx)   
    redis.set("my", cy)     
    img = get_current_spot()   
    pixel = img.getpixel((cx, cy))
    color = rgb_to_hex(pixel)
    redis.set("color", color)
    socketio.emit('picked_color', color)

# '''
#     msg.channel 
#     msg.data
# '''
def event_trends_handler(msg):
    print(f"flask event_trends_handler {msg} --------------------------- ")
    emit('tags', msg)
  
if __name__ == '__main__':
    print("start flask 1.1.0") 

    socketio.run(app, host='0.0.0.0', allow_unsafe_werkzeug=True, debug=True)