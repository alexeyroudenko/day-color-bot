import os
import telebot
bot = telebot.TeleBot('1704471935:AAFFqVM3qu8dkjkO0Feg00vR-WSw_4rJJC0')

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id, 'Привет, погнали!')
	with open("chat_ids.txt", "a") as text_file:
		text_file.write("%s\n" % (message.chat.id))
		text_file.close()
	os.system("sort chat_ids.txt | uniq | sponge chat_ids.txt")


@bot.message_handler(commands=['1'])
def id_message(message):
    bot.send_message(message.chat.id, message.chat.id)


bot.polling(none_stop=True, interval=0)
