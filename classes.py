import configparser

from datetime import datetime

import peewee as pw
from peewee import *

config = configparser.ConfigParser()
config.read('config/db.ini')

socket = None

if int(config['DEFAULT']['use_socket']):
    socket = '/run/mysqld/mysqld.sock'

db = pw.MySQLDatabase(config['DEFAULT']['db'], host='localhost', port=3306, user=config['DEFAULT']['user'],
                      password=config['DEFAULT']['password'], unix_socket=socket)


class MySQLModel(Model):
    class Meta:
        database = db


class Player(MySQLModel):
    id = PrimaryKeyField(unique=True)
    tg_id = IntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    created = DateTimeField(default=datetime.now)
    questions_attempted = IntegerField(default=0)
    questions_correct = IntegerField(default=0)
    total_score = BigIntegerField(default=0)

    def name(self):
        if self.username:
            return self.username
        else:
            return self.first_name

    def check_info(self, tg_player):

        changes = False

        if not self.username and tg_player['username'] != '':
            self.username = tg_player['username']
            changes = True
        if not self.first_name and tg_player['first_name'] != '':
            self.first_name = tg_player['first_name']
            changes = True
        if not self.last_name and tg_player['last_name'] != '':
            self.last_name = tg_player['last_name']
            changes = True

        if changes:
            self.save()


class Question(MySQLModel):

    id = PrimaryKeyField(unique=True)
    question = TextField()
    created = DateTimeField(default=datetime.now)
    answer = TextField()
    answer_type = IntegerField(default=0)
    group = CharField(null=True)
    active = BooleanField(default=True)


class QuestionHistory(MySQLModel):
    id = PrimaryKeyField(unique=True)
    question = ForeignKeyField(Question, related_name='questions')
    hint_1 = CharField(null=True)
    hint_2 = CharField(null=True)
    hint_3 = CharField(null=True)
    created = DateTimeField(default=datetime.now)
    winner = ForeignKeyField(Player, related_name='winners', null=True)
    score_change = IntegerField(null=True)


class Event(MySQLModel):
    id = PrimaryKeyField(unique=True)
    player = ForeignKeyField(Player, related_name='players')
    question = ForeignKeyField(QuestionHistory, related_name='answered_questions')
    description = CharField(null=True)
    attempts = IntegerField(null=True)  # TODO: Register attempts?
    score_change = IntegerField(null=True)


class Round(MySQLModel):
    id = PrimaryKeyField(unique=True)
    started = DateTimeField(default=datetime.now)
    ended = DateTimeField(null=True)


def test_values():

    # Try to select player
    try:
        with db.atomic():
            p = Player.get(Player.id == 153475046)
            print("Player already created at " + str(p.created))
    except DoesNotExist:
        print("Player doesn't exist!")

        # No entry - create new player
        with db.atomic():
            Player.create(id=153475046)
            p = Player.get(Player.id == 153475046)
            print("Created new player at " + str(p.created))


# Create the tables.
# db.create_tables([Player, Event, Question, QuestionHistory, Round], safe=True)
db.drop
# Run test values
# test_values()
