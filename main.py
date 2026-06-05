
import logging
import logging.handlers
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import os
import time
import re
import glob
import os

class TColorBot:
    SHHH_API_KEY: str
    SHHH_MY_CHAT_ID: str
    chat_ids_file:str 

    
    logFormat = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        format=logFormat,
        level=logging.INFO,
    )

    chat_ids_file = "data/chat_ids.txt"
    httpx_logger = logging.getLogger("httpx")
    

    # Set the logging level to WARNING to ignore INFO and DEBUG logs
    httpx_logger.setLevel(logging.WARNING)
    def removefile(self, f):
        try:
            os.remove(f)
        except OSError:
            pass

    def startBot(self):
        exitt = False
        if self.SHHH_API_KEY == None:
            logging.info("SHHH_API_KEY must be defined")
            exitt = True
        logging.info("SHHH_MY_CHAT_ID       : %s", self.SHHH_MY_CHAT_ID)
        if not exitt:
            application = ApplicationBuilder().token(self.SHHH_API_KEY).build()
            logging.info("Starting bot")
            start_handler = CommandHandler("start", self.start)
            application.add_handler(start_handler)
            application.add_handler(CommandHandler("me", self.me_cmd))
            application.add_handler(CommandHandler("now", self.now_cmd))

            unknown_handler = MessageHandler(filters.COMMAND, self.unknown)
            application.add_handler(unknown_handler)
            application.add_handler(MessageHandler(filters.TEXT, self.handle_text_message))
            application.run_polling(allowed_updates=Update.ALL_TYPES)
            # self.send_message(chat_id=self.SHHH_MY_CHAT_ID, text="Started")
            logging.info("Bot await messages")
        else:
            logging.info("Failed to run, please resolve exports issue and run again")
        
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
    
    #
    #
    #   
    async def me_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = f"{update.effective_chat.id}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
        logging.info("me_cmd - effective chat id: %s", update.effective_chat.id)

    async def now_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        list_of_files = glob.glob('out/*_blr.png')
        latest_file = max(list_of_files, key=os.path.getctime)
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(latest_file, 'rb'))
        logging.info("now_cmd - effective chat id: %s", update.effective_chat.id)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = f"Please wait until tomorrow morning, or use command '/now' or ask me word color 'word' {update.effective_chat.id}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
        logging.info("start - effective chat id: %s - txt: %s", update.effective_chat.id, txt)

        with open(self.chat_ids_file, "a") as text_file:
            text_file.write("%s\n" % (update.effective_chat.id))
            text_file.close()
        
        logging.info(f"save to  {self.chat_ids_file} - effective chat id: %s", update.effective_chat.id)
        
    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        txt = "Sorry, I didn't understand that command."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=txt)
        logging.info("unknown - effective chat id: %s - txt: %s", update.effective_chat.id, txt)


    async def handle_text_message(self, update, context):
        username = str(update.message.chat.username)
        start = time.time()
        logging.info("Started processing for "+username)
        
        try:
            from color_worker import ColorBot
            color = ColorBot()
            color.start(update.message.text)
            color.step()
            color.make_collage()
            result = color.make_spot() 
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(result, 'rb'))

        except Exception as e :
            end = time.time()
            logging.log(logging.ERROR,str(end-start) + " " + username + " : " + str(update.effective_chat.id)  + " : FAIL UNKNOWN : Failed processing message")
            logging.log(logging.ERROR,str(e))
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Failure processing your message")



if __name__ == '__main__':
    bot = TColorBot()
    bot.SHHH_API_KEY = os.getenv('SHHH_API_KEY')
    bot.SHHH_MY_CHAT_ID = os.getenv('SHHH_MY_CHAT_ID')
    bot.startBot()

