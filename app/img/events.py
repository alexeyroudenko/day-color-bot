import logging
import logging.handlers

logging.basicConfig(
    format="%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger('tags')


'''
Event converted to websocket
'''
class Event():
    
    waiting_word = False
    waiting_word_stop = False
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