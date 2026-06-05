# -*- coding: utf-8 -*-
#!/usr/bin/env python3

import telebot
bot = telebot.TeleBot('1704471935:AAFFqVM3qu8dkjkO0Feg00vR-WSw_4rJJC0')

import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# file = open('/chat_ids.txt', 'r')
# for line in file:
#     bot.send_message(int(line.strip()), global_polarity)

path = "/home/jay/twimg/out/"

files = [os.path.join(path, fn) for fn in os.listdir(path)]
images = [fn for fn in files if os.path.splitext(fn)[1].lower() in ('.jpg', '.jpeg', '.png')]
latest_file = max(images, key=os.path.getmtime)

file = open('chat_ids.txt', 'r')
for line in file:
	img = open(latest_file, 'rb')
	# bot.send_message(int(line.strip()), global_polarity)
	try:
		bot.send_photo(int(line.strip()), img)
	except Exception as e:
		#logging.error(traceback.format_exc())
		print(e)
		# Logs the error appropriately. 

# imageFile = "colors.jpg"
# img = open(latest_file, 'rb')
# bot.send_photo(218014682, img)
# bot.send_message(218014682, global_polarity)
# 218014682
# bot.polling()