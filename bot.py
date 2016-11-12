import logging
from time import sleep

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                             level=logging.INFO)


updater = Updater(token='')
dispatcher = updater.dispatcher


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Welcome to Kanapasta Trivia! Trivia will start in:")

    c = 3

    while c:
        bot.sendMessage(chat_id=update.message.chat_id, text= str(c) + " ...")
        c -= 1
        sleep(1)


def echo(bot, update):
    logging.info('message received: ' + str(update.message.text) + str(update.message.chat_id))
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)


def caps(bot, update, args):
    text_caps = ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)


def main():
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)

    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    updater.start_polling()


main()
