from time import sleep

from db import Player as Player_db

# {'id': , 'last_name': '', 'first_name': '', 'type': '', 'username': ''}


class Player:

    def __init__(self, tg_instance, bot, chat_id):

        self.player, created = Player_db.get_or_create(tg_id=tg_instance['id'])
        self.tgi = tg_instance

        if created:
            sleep(2)
            print("Created new player " + self.get_player_name())
            bot.sendMessage(chat_id=chat_id, text="Registered new player " + self.get_player_name() + ', welcome!')

    def get_player_name(self):
        if self.tgi['username'] != '':
            return self.tgi['username']
        else:
            return self.tgi['first_name']
