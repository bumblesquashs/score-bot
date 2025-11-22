import re
import database.db as database
from database.db_arguments import RecordMessageData

plus_two_triggers = ['plus 2', '+2']
minus_two_triggers = ['minus 2', '-2']


def filter_message(message_text):
    filter_text = message_text.lower()
    return filter_text


class Actioner:
    """
    Run actions based on message and react events
    """

    def __init__(self, original_message, reply_message):

        self.channel = reply_message.channel

        self.original_message = original_message.content
        self.reply_message = reply_message.content

        self.original_filtered = filter_message(self.original_message)
        self.reply_filtered = filter_message(self.reply_message)

        self.original_username = str(original_message.author)
        self.reply_username = str(reply_message.author)

        self.original_discord_id = str(original_message.author.id)
        self.reply_discord_id = str(reply_message.author.id)

    async def action_message(self):
        if self.is_plus_two(self.reply_filtered):
            self.run_plus_two()
            await self.channel.send('Noted - plus')
            return

        if self.is_minus_two(self.reply_filtered):
            self.run_minus_two()
            await self.channel.send('Noted - minus')

    
    async def action_react(self):
        pass


    def is_plus_two(self, message: str) -> bool:
        for prompt in plus_two_triggers:
            if prompt in message:
                return True
        return False


    def is_minus_two(self, message: str) -> bool:
        for prompt in minus_two_triggers:
            if prompt in message:
                return True
        return False
    

    def run_plus_two(self):
        database.record_message(
                RecordMessageData(points=2, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.original_discord_id, 
                                  message_text=self.original_message))


    def run_minus_two(self):
        database.record_message(
                RecordMessageData(points=-2, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.original_discord_id, 
                                  message_text=self.original_message))
