import logging
import logging.handlers

logging.basicConfig(
    format="%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('tags')  



# import websockets
# import asyncio
# import asyncio
# import websockets
# from websockets import ConnectionClosed


# CLIENTS = set()
# async def handler(websocket):
#     CLIENTS.add(websocket)
#     try:
#         await websocket.wait_closed()
#     finally:
#         CLIENTS.remove(websocket)

# async def broadcast(message):
#     print("broadcast", message)
#     for websocket in CLIENTS.copy():
#         try:
#             await websocket.send(message)
#         except ConnectionClosed:
#             pass

# async def broadcast_messages():
#     while True:
#         await asyncio.sleep(1)
#         message = "hello"  # your application logic goes here
#         await broadcast(message)

# async def main():
#     async with websockets.serve(handler, "localhost", 8765):
#         #await asyncio.Future()  # run forever
#         await broadcast_messages()


'''
Event converted to websocket
'''
class Event():
    
    waiting_word = False
    observer = None
    count = 0
    
    def send(self, *args):
        self.observer.listen(*args)            
        self.count += 1           
        
                
'''


'''
class Observer():
    
    def __init__(self, event):
        self._observers = []
        self.event = event
        self.event.observer = self

    def notify(self, args):
        """Alert the observers"""
        for observer in self._observers:
            # if modifier != observer:
            observer.on_event(args)

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass
        
    def listen(self, *args):
        msg = args[0]
        self.notify(args)





from pythonosc.udp_client import SimpleUDPClient

'''


'''
class OSCsender():
    
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 8888
        self.client = SimpleUDPClient("127.0.0.1", self.port)

    def on_event(self, args):
        msg = args[0]
        if msg == "tag":
            tag_cmd = args[1]
            tag_str = args[2]
            #tag_id = args[3]
            # logging.info(f"send osc {msg}-{tag_cmd}-{tag_str}")
            self.client.send_message("/" + msg, [tag_cmd, tag_str])            
        if msg == "img":
            cmd = args[1]
            if len(args)>2:
                path = args[2]
                logging.info(f"send osc {msg}-{cmd}-{path}")
                self.client.send_message("/" + msg, [cmd, path])
            else:
                logging.info(f"send osc {msg}-{cmd}")
                
        if msg == "msg":
            cmd = args[1]
            msgg = args[2]
            # logging.info(f"send osc {msg}-{cmd}-{msg}")            
            self.client.send_message("/" + msg, [cmd, msg])
