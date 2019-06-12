from time import sleep
from random import randint

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Job

from models import *

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO, filename='trivia.log')

# logging.basicConfig(filename='example.log',level=logging.DEBUG)

config = configparser.ConfigParser()
config.read('config/trivia.ini')


class Trivia:

    def __init__(self, profile='DEFAULT'):

        self.profile = profile

        self.updater = Updater(token=config[self.profile]['bot_token'])
        self.bot = self.updater.bot
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        self.chat_id = config[self.profile]['trivia_chat']
        self.active = False
        self.question = None
        self.current_answer = None
        self.players_with_attempts = None
        self.points = None
        self.correct = False
        self.round = None

        self.webhook = int(config[self.profile]['webhook'])
        self.prepare()

    def create_start_handler(self):

        def start(bot, update):

            if self.active:
                bot.sendMessage(chat_id=update.message.chat_id, text="Trivia is already running!")
            else:
                self.round = Round()

                db.connect()
                self.round.save()
                db.close()

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

                self.job_queue.run_once(play_game, 0)

        start_handler = CommandHandler('start', start)
        self.dispatcher.add_handler(start_handler)

    def create_stop_handler(self):

        def stop(bot, update):

            if self.active:
                self.round.ended = datetime.now()

                db.connect()
                self.round.save()
                db.close()

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
                tg_player = update.message.from_user

                db.connect()

                player, created = Player.get_or_create(tg_id=tg_player['id'])
                player.check_info(tg_player)

                if created:
                    bot.sendMessage(chat_id=self.chat_id,
                                    text="Registered new player {}, welcome!".format(player.name()))

                self.players_with_attempts.append(player)

                if (message.lower() == self.current_answer.lower()) and (not self.correct):
                    self.correct = True

                    player.total_score += self.points
                    player.questions_correct += 1
                    self.question.winner = player
                    self.question.score_change = self.points

                    player.save()
                    self.question.save()

                    for player in self.players_with_attempts:
                        player.questions_attempted += 1
                        player.save()

                    bot.sendMessage(chat_id=update.message.chat_id,
                                    text="{} got it! {} points have been added. The correct answer was {}.".format(
                                        player.name(), self.points, self.current_answer))

                    # TODO: Some highlights from the round?

                db.close()

        answer_handler = MessageHandler(Filters.text, answer)
        self.dispatcher.add_handler(answer_handler)

    def create_stats_handler(self):

        def stats(bot, update):

            db.connect()

            message = "Questions attempted\n"
            for player in Player.select().order_by(Player.questions_attempted.desc()):
                name = player.name()
                score = player.questions_attempted

                message_row = "{}: {}\n".format(name, score)
                message += message_row

            message += "\nQuestions correct\n"
            for player in Player.select().order_by(Player.questions_correct.desc()):
                name = player.name()
                score = player.questions_correct

                message_row = "{}: {}\n".format(name, score)
                message += message_row

            message += "\nTotal score\n"
            for player in Player.select().order_by(Player.total_score.desc()):
                name = player.name()
                score = player.total_score

                message_row = "{}: {}\n".format(name, score)
                message += message_row

            db.close()

            bot.sendMessage(chat_id=update.message.chat_id, text=message)

        stats_handler = CommandHandler('stats', stats)
        self.dispatcher.add_handler(stats_handler)

    def create_whoami_handler(self):

        def whoami(bot, update):
            tg_player = update.message.from_user

            print("ID:\t\t\t\t{}".format(tg_player.id))
            print("Username:\t\t{}".format(tg_player.username))
            print("First name:\t\t{}".format(tg_player.first_name))
            print("Last name:\t\t{}".format(tg_player.last_name))
            # print("Type:\t\t{}".format(tg_player.type))

        whoami_handler = CommandHandler('whoami', whoami)
        self.dispatcher.add_handler(whoami_handler)

    def prepare(self):

        # Create handlers
        self.create_start_handler()
        self.create_stop_handler()
        self.create_answer_handler()
        self.create_stats_handler()
        self.create_whoami_handler()

        # Start webhook or poller

        if self.webhook:
            print("Webhook enabled. Initializing ...")
            self.updater.start_webhook(listen='0.0.0.0',
                                       port=8443,
                                       url_path='TOKEN',
                                       key='server.key',
                                       cert='server.pem',
                                       webhook_url=config['DEFAULT']['webhook_address'])
        else:
            print("Starting poller ...")
            self.updater.start_polling(timeout=30)

        self.bot.sendMessage(chat_id=self.chat_id, text="Trivia instance ready.")

    @staticmethod
    def get_a_random_question():

        db.connect()
        q = Question.select().where(Question.active).order_by(fn.Rand()).limit(1).get()
        db.close()

        return q

    @staticmethod
    def generate_hints(answer):

        a = answer
        l = len(a)

        if l == 1:
            return ['*']

        elif l == 2:

            h = ['**']
            if randint(0, 1) == 0:
                h.append('*' + a[1])
            else:
                h.append(a[0] + '*')

            return h

        elif 3 <= l <= 5:
            hints = list()
            hint = list()

            for i in range(l):
                if a[i] != ' ':
                    hint.append('*')
                else:
                    hint.append(' ')

            hints.append("".join(hint))

            hint = list()

            for i in range(l):
                if (randint(0, 2) == 0) or a[i] == ' ':
                    hint.append(a[i])
                else:
                    hint.append('*')

            hints.append("".join(hint))

            return hints

        else:
            hints = list()

            hint = list()

            for i in range(l):
                if a[i] != ' ':
                    hint.append('*')
                else:
                    hint.append(' ')

            hints.append("".join(hint))

            hint = list()

            for i in range(l):
                if (randint(0, 1) == 0) or a[i] == ' ':
                    hint.append(a[i])
                else:
                    hint.append('*')

            hints.append("".join(hint))

            hint_comp = hint
            hint = list()

            for i in range(l):
                if (randint(0, 1) == 0) or a[i] == ' ' or hint_comp[i] != '*':
                    hint.append(a[i])
                else:
                    hint.append('*')

            hints.append("".join(hint))

            return hints

    def ask_question(self):

        question = self.get_a_random_question()
        hints = self.generate_hints(question.answer)

        qh = QuestionHistory()
        qh.question = question

        self.question = qh

        i = 1

        for hint in hints:
            if i == 1:
                qh.hint_1 = hint
            elif i == 2:
                qh.hint_2 = hint
            elif i == 3:
                qh.hint_3 = hint
            i += 1

        # Store created question to history
        db.connect()
        qh.save()
        db.close()

        self.correct = False
        self.points = 10
        self.current_answer = question.answer
        self.players_with_attempts = []

        self.bot.sendMessage(chat_id=self.chat_id, text="Question #" +
                                                        str(question.id) +
                                                        " :: " + question.question + " :: "
                                                        + str(self.points) + " points")
        sleep(10)

        for hint in hints:
            if not self.correct:
                self.points -= 2
                self.bot.sendMessage(chat_id=self.chat_id, text="Hint :: " + hint + " :: "
                                                                + str(self.points) + " points")
                sleep(20)

        if not self.correct:
            self.current_answer = None
            self.correct = False
            self.bot.sendMessage(chat_id=self.chat_id, text="No-one got it! The correct answer was " +
                                                            question.answer)

            db.connect()
            for player in self.players_with_attempts:
                player.questions_attempted += 1
                player.save()
            db.close()

        sleep(10)

    def play(self):

        while self.active:
            self.ask_question()

        self.end_play()

    def end_play(self):
        self.bot.sendMessage(chat_id=self.chat_id, text="Game over. Thanks for playing!")

        # TODO: Store status to db, show statistics, etc.
        print("End game.")


if __name__ == '__main__':
    Trivia()
