import re
import random
from math import ceil

import database.db as database
from database.db_arguments import RecordMessageData

plus_two_triggers = ['plus 2', '+2']
minus_two_triggers = ['minus 2', '-2']


def parse_arbitrary(message: str):
    """
    Detect patterns like:
        "plus 1", "plus 13", "plus 2.5",
        "+7", "+92", "+3.8"
        "minus 2", "minus 14", "minus 1.3",
        "-7", "-92", "-3.8"
    but NOT:
        "plus -2.4", "3", "hello", etc.

    Returns float if match, else None.

    REGEX expressions grabbed from GPT
    """
    string = message.strip().lower()

    # Pattern 1: "plus X" where X is a positive integer or float
    match = re.fullmatch(r"plus\s+([0-9]+(?:\.[0-9]+)?)", string)
    if match:
        return float(match.group(1))

    # Pattern 2: "+X" where X is a positive integer or float
    match = re.fullmatch(r"\+([0-9]+(?:\.[0-9]+)?)", string)
    if match:
        return float(match.group(1))
    
    # Pattern 3: "minus X" where X is a positive integer or float
    match = re.fullmatch(r"minus\s+([0-9]+(?:\.[0-9]+)?)", string)
    if match:
        return float(match.group(1))

    # Pattern 4: "-X" where X is a positive integer or float
    match = re.fullmatch(r"\-([0-9]+(?:\.[0-9]+)?)", string)
    if match:
        return float(match.group(1))

    return None


def filter_message(message_text):
    filter_text = message_text.lower().strip()
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
            await self.channel.send('Noted.')
            return

        if self.is_minus_two(self.reply_filtered):
            self.run_minus_two()
            await self.channel.send('Noted.')

        if quantity := parse_arbitrary(self.reply_filtered):
            print(f'debug: parsed {quantity}')
            await self.run_arbitrary(quantity)

    
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
        

    
    async def run_arbitrary(self, quantity: float):
        sarcasm = [
            "it'll be a cold day in hell before i allow your stupid-ass FLOATS into my leaderboard, you conniving weasel",
            f"oh look, {self.reply_username} thinks they're being cute by trying to give non-integer amounts of points. how pathetic.",
            f"{quantity}? really? you're lucky i dont -2 your ass for trying that shit"
            f"is this the fucking world we live in? where discord addicts dont even have the BACKBONE to use whole numbers of points. god."
            f"trust me buddy. just round it up. you don't need to equivocate. {int(ceil(quantity))} would have done just fine."
            f"howabout no. that better be the last time i see a decimal point or YOU'LL BE SORRY. I KNOW WHERE YOU LIVE."
            f"try all you want, i am NOT moving us off of the Abby-Squash System. You say 'fractional reserve pointing', i hear 'confidently incorrect simpleton'"
            f"INTEGERS ONLY. who do you think i am? a 5th grader??? decimals aren't real math. go take a calculus class and tell me how many decimals you see."
            f"Decimals are not valid input for this opreation. Upset about it? Too bad. That's life, buddy. Maybe file a complaint with the hospital from which you were born."
        ]

        if not quantity.is_integer():
            await self.channel.send(random.choice(sarcasm))
            return

        quantity = int(quantity)

        if quantity > 6 or quantity < -6:
            await self.channel.send('Hey. Not too much.')
            return
        
        database.record_message(
                RecordMessageData(points=quantity, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.original_discord_id, 
                                  message_text=self.original_message))
        
        if random.random() > 0.4:
            await self.channel.send("I'll allow it, but I prefer you give +2 or -2. I might not always be so kind.")
            return
        
        if random.random() > 0.5:
            database.record_message(
                RecordMessageData(points=-1, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.reply_discord_id, 
                                  message_text=''))
            await self.channel.send("I'll allow it, but since it wasn't +2 or -2, It's gonna cost ya. -1 point.")
            return
        
        await self.channel.send("I'll allow it, but since it wasn't +2 or -2, It's gonna cost ya. -2 points.")

        database.record_message(
                RecordMessageData(points=-2, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.reply_discord_id, 
                                  message_text=''))


        

