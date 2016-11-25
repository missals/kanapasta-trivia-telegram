import configparser
import datetime

import peewee as pw
from peewee import *

config = configparser.ConfigParser()
config.read('config/db.ini')

db = pw.MySQLDatabase(config['DEFAULT']['db'], host='localhost', port=3306, user=config['DEFAULT']['user'],
                      password=config['DEFAULT']['password'], unix_socket='/run/mysqld/mysqld.sock')


def before_request_handler():
    db.connect()


def after_request_handler():
    db.close()


class MySQLModel(Model):
    class Meta:
        database = db


class Player(MySQLModel):
    id = PrimaryKeyField(unique=True)
    tg_id = IntegerField(unique=True)
    created = DateTimeField(default=datetime.datetime.now)
    questions_attempted = IntegerField(default=0)
    questions_correct = IntegerField(default=0)
    total_score = BigIntegerField(default=0)


class Question(MySQLModel):
    id = PrimaryKeyField(unique=True)
    question = TextField()
    created = DateTimeField(default=datetime.datetime.now)
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
    created = DateTimeField(default=datetime.datetime.now)
    score_change = IntegerField(null=True)


class Event(MySQLModel):
    id = PrimaryKeyField(unique=True)
    player = ForeignKeyField(Player, related_name='players')
    question = ForeignKeyField(QuestionHistory, related_name='answered_questions')
    description = CharField(null=True)
    attempts = IntegerField(null=True)
    score_change = IntegerField(null=True)


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
# db.create_tables([Player, Event, Question, QuestionHistory], safe=True)

# Run test values
# test_values()
