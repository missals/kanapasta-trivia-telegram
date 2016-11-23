import configparser

from time import sleep

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job

from question import *

# TODO: Logging

config = configparser.ConfigParser()
config.read('config/trivia.ini')


class Trivia:

    def __init__(self):

        self.updater = Updater(token=config['DEFAULT']['bot_token'])
        self.bot = self.updater.bot
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        self.chat_id = config['DEFAULT']['trivia_chat']
        self.current_answer = None
        self.correct = False
        self.active = False

        self.start_webhook()
        self.bot.sendMessage(chat_id=self.chat_id, text="Trivia instance ready.")

    def create_start_handler(self):

        def start(bot, update):

            if self.active:
                bot.sendMessage(chat_id=update.message.chat_id, text="Trivia is already running!")
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text="Trivia will start in ...")

                sleep(1)
                c = 3

                while c >= 1:
                    bot.sendMessage(chat_id=update.message.chat_id, text=str(c) + " ...")
                    sleep(1)
                    c -= 1

                # Time to play the game!
                self.active = True

                def play_game(bot, job):
                    self.play()

                self.job_queue.put(Job(play_game, 0, repeat=False))

        start_handler = CommandHandler('start', start)
        self.dispatcher.add_handler(start_handler)

    def create_stop_handler(self):

        def stop(bot, update):

            if self.active:
                bot.sendMessage(chat_id=update.message.chat_id, text="Trivia will end after this round.")
                self.active = False
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text="What should I stop exactly?")

        stop_handler = CommandHandler('stop', stop)
        self.dispatcher.add_handler(stop_handler)

    def create_answer_handler(self):

        def answer(bot, update):
            if self.current_answer:
                message = update.message.text

                if message.lower() == self.current_answer.lower():
                    self.correct = True

                    # TODO: Implement proper method to save stats etc. with the player. Some highlights from the round?
                    bot.sendMessage(chat_id=update.message.chat_id, text=str(update.message.from_user['username']) + " got it!")

        answer_handler = MessageHandler(Filters.text, answer)
        self.dispatcher.add_handler(answer_handler)

    def start_webhook(self):

        # Create handlers
        self.create_start_handler()
        self.create_stop_handler()
        self.create_answer_handler()

        # Start updater
        # self.updater.start_polling()

        # Start webhook
        self.updater.start_webhook(listen='0.0.0.0',
                                   port=8443,
                                   url_path='TOKEN',
                                   key='server.key',
                                   cert='server.pem',
                                   webhook_url=config['DEFAULT']['webhook_address'])

    def ask_question(self):
        q = Question()
        self.current_answer = q.question['answer']

        self.bot.sendMessage(chat_id=self.chat_id, text="Question #" +
                                                        str(q.question['qid']) +
                                                        ": " + q.question['question'])
        sleep(5)

        for hint in q.question['hints']:
            if not self.correct:
                self.bot.sendMessage(chat_id=self.chat_id, text="Hint: " + hint)
                sleep(10)

        if not self.correct:
            self.bot.sendMessage(chat_id=self.chat_id, text="No-one got it! The correct answer was " +
                                                            q.question['answer'])

        self.correct = False
        self.current_answer = None

    def play(self):

        while self.active:
            self.ask_question()

        self.end_play()

    def end_play(self):
        self.bot.sendMessage(chat_id=self.chat_id, text="Game over. Thanks for playing!")

        # TODO: Store status to db, show statistics, etc.
        print("End game.")

Trivia()
