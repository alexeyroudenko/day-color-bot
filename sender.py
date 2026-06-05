# -*- coding: utf-8 -*-
# !/usr/bin/env python3

import sys
import logging
import logging.handlers
log_file_name = f"sender.log"
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    handlers=[
                        logging.FileHandler(log_file_name),
                        logging.StreamHandler(sys.stdout)
                    ],
                    # filemode='a',
                    encoding='utf-8',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

import time
import datetime
import glob
import os
from datetime import datetime

import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


#------------------------------------------------------------------------------
#
#
#------------------------------------------------------------------------------
while True:
        try:
            now = datetime.now()
            print(now.hour, now.minute)
            if now.hour == 12 and now.minute == 1:
                print("send")
                list_of_files = glob.glob('out/*_blr.png')
                latest_file = max(list_of_files, key=os.path.getctime)
                logging.info(f"latest_file: {latest_file}")

                import telebot
                bot = telebot.TeleBot('1704471935:AAFFqVM3qu8dkjkO0Feg00vR-WSw_4rJJC0')

                file = open('data/chat_ids.txt', 'r')
                for line in file:
                    chat_id = int(line.strip())
                    try:
                        img = open(latest_file, 'rb')
                        bot.send_photo(int(line.strip()), img)
                    except Exception as e:
                        logging.error(chat_id, e)

                bot.polling()
                time.sleep(60*60*6)
            else:
                time.sleep(1)
                 
        except Exception as inst:
            logging.error(type(inst))   
            logging.error(inst.args)     
            logging.error(inst) 
