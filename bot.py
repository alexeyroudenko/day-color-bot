
import logging
import logging.handlers
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import os
import time
import re
import glob
import os
import datetime, pytz
import os

from tags import retrieve_trends
from controller import Runner   

import yaml
with open('config.yml', 'r') as file:
    cfg = yaml.safe_load(file)
       
class TColorBot:
    
    API_KEY: str
    MY_CHAT_ID: str
    chat_ids_file:str = cfg['app']['chat_ids']
    tmp_folder:str = cfg['app']['tmp_folder']
    
    logger = logging.getLogger('bot')
    httpx_logger = logging.getLogger("httpx")
    # # Set the logging level to WARNING to ignore INFO and DEBUG logs
    # httpx_logger.setLevel(logging.WARNING)
    
    def get_latest_out(self):
        list_of_files = glob.glob(cfg['app']['spot_folder'] + '/*_blr.png')
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    
    def removefile(self, f):
        try:
            os.remove(f)
        except OSError:
            pass



    def startBot(self):
        self.runer = Runner()
        exitt = False
        if self.API_KEY == None:
            logging.info("API_KEY must be defined")
            exitt = True
        logging.info("MY_CHAT_ID       : %s", self.MY_CHAT_ID)
        if not exitt:
            application = ApplicationBuilder().token(self.API_KEY).build()
            self.application = application
            logging.info("Starting bot")
            start_handler = CommandHandler("start", self.start)
            application.add_handler(start_handler)
            application.add_handler(CommandHandler("me", self.me_cmd))
            application.add_handler(CommandHandler("now", self.now_cmd))
            unknown_handler = MessageHandler(filters.COMMAND, self.unknown)
            application.add_handler(unknown_handler)
            application.add_handler(MessageHandler(filters.TEXT, self.handle_text_message))
            
            job = application.job_queue
            # job.run_repeating(self.a_ping, interval=10.0, first=0.0)
            job.run_repeating(self.a_collect, interval=cfg['app']['sleep_time'], first=1)
            #job.run_daily(self.a_daily_job, datetime.time(hour=10, minute=0), days=(0,1,2,3,4,5,6))
            
            #job.run_repeating(self.a_daily_job, interval=1.0*60.0, first=0.0)            
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            logging.info("Bot await messages")
        else:
            logging.info("Failed to run, please resolve exports issue and run again")
        
    async def a_ping(self, context):
        logging.info(f"a_ping {context}")
        await context.bot.send_message(chat_id=self.MY_CHAT_ID, text='a_ping')
        
    async def a_collect(self, context):
        logging.info(f"a_collect {context}")
        start = time.time()
        try:            
            trends = retrieve_trends()           
            self.runer.loop(trends)                            
            logging.log(f"trends {trends}")
                                    
            end = time.time()        
        except Exception as e :
            end = time.time()
            logging.log(logging.ERROR,str(e))
                
    
    
    async def handle_text_message(self, update, context):
        username = str(update.message.chat.username)
        start = time.time()
        try:            

            #msg = "Started processing for " + username + f" and {update.effective_chat.id} with " + update.message.text
            #msg = update.message.text
            #logging.info(msg)
            #await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
            query = update.message.text            
            self.runer.process_msg(query) 
            while self.runer.event.waiting_word == True:
                time.sleep(0.5)
            while self.runer.event.waiting_word_spot == True:
                time.sleep(0.5)                
            spot_path = self.runer.spot_path    
            
            
            end = time.time()
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(spot_path, 'rb'))
        
        except Exception as e :
            end = time.time()
            logging.log(logging.ERROR,str(e))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Failure processing your message")    
    
    

    
    
    #
    #
    #
    #
    async def a_daily_job(self, context):
        logging.info(f"a_daily_job {context}")        
        file = open(self.chat_ids_file, 'r')
        latest_file = self.get_latest_out()
        for line in file:
            chat_id = line.strip()
            try:
                await context.bot.send_photo(chat_id=chat_id, photo=open(latest_file, 'rb'))
            except Exception as e:
                logging.error(chat_id, e)
        #await context.bot.send_message(chat_id=self.SHHH_MY_CHAT_ID, text='a_daily_job')

    def _esc_char(self,match):
        return '\\' + match.group(0)

    def my_escape(self,name):
        return re.compile(r'\s|[]()[]').sub(self._esc_char, name)

    def checkUser(self, chat_id: str, allowed_chat_id_string: str):
        if allowed_chat_id_string is None:
            return True
        allow_list = allowed_chat_id_string.split(' ')
        if any(chat_id == value for value in allow_list):
            return True
        logging.info("SHHH_ALLOWED_CHAT_IDS : Not processing for %s \nAllowList %s", chat_id, allow_list)
        return False
    
    async def me_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{update.effective_chat.id}")

    async def now_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(self.get_latest_out(), 'rb'))

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = f"Please wait until tomorrow morning, or use command '/now' or ask me word color 'word' {update.effective_chat.id}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
        logging.info("start - effective chat id: %s - txt: %s", update.effective_chat.id, txt)

        with open(self.chat_ids_file, "a") as text_file:
            text_file.write("%s\n" % (update.effective_chat.id))
            text_file.close()
            os.system(f"sort {self.chat_ids_file} | uniq | sponge {self.chat_ids_file}")
        
        logging.info(f"save to {self.chat_ids_file} - effective chat id: %s", update.effective_chat.id)
        
    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="unknown")        





if __name__ == '__main__':
    
    # set code directory    
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    bot = TColorBot()
    bot.API_KEY = os.getenv('SHHH_API_KEY')
    bot.MY_CHAT_ID = os.getenv('SHHH_MY_CHAT_ID')
    bot.startBot()