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
    id = IntegerField(primary_key=True, unique=True)
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


class Event(MySQLModel):
    id = PrimaryKeyField(unique=True)
    player = ForeignKeyField(Player, related_name='events')
    question = ForeignKeyField(Question, related_name='questions')
    created = DateTimeField(default=datetime.datetime.now)
    description = CharField()
    score_change = IntegerField()

    class Meta:
        indexes = (
            (('player', 'created'), False),
        )


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


# Connect to our database.
# db.connect()

# Create the tables.
# db.create_tables([Player, Event, Question], safe=True)

# Run test values
# test_values()

# Close connection.
# db.close()
