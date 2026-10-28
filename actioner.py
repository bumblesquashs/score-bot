import re
import random
from math import ceil

import database.db as database
from database.db_arguments import RecordMessageData

plus_two_triggers = ['plus 2', '+2']
minus_two_triggers = ['minus 2', '-2']
zero_triggers = ['plus 0', 'minus 0', '+0', '-0', '±0']

hexdumps = [
    '"i used to collect worms as a kid and set them on fire" - justin',
    '"so sinful but oh-so silky-smooth" - brian',
    '"this sausage farmers wrap is so soft and warm it feels like i\'m eating a living person" - abby',
    '"you\'re gonna have to try a little harder if you wanna make me moan" - kaiden',
    '"i think you need more lesbians in your life" - patrick johnstone to angela',
    '"I didn\'t realize there was a city called Nelson" - ruofan',
    '"it\'s my god given right to drink piss" - watchy',
    '"i wanna be a queer trauma-informed land speculator" - angela',
    '"kaiden why do you want to bomb bc childrens hospital?" - michael',
    '"boycott metro vancouver by taking a dump on the sidewalk" - bowie',
    '"had two singles a triple a walk a flyout a groundout and one ground ball taken straight to my groin" - will'
    '"many of you in this server would be better suited to a life of scavenging debris off the ocean floor with some sort of tentacle appendage" - ahasan',
]

def special_hexdump(input: str):
    width = 8
    try:
        raw = input.encode("utf-8")
    except UnicodeEncodeError as e:
        raise ValueError(f"String is not valid UTF-8: {e}") from e
    
    lines = []
    for offset in range(0, len(raw), width):
        chunk = raw[offset:offset + width]
        lines.append(" ".join(f"{b:02x}" for b in chunk).ljust(width * 3 - 1))
    hexdump = "\n".join(lines).strip()
    result = f'```{hexdump}```'
    return result



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

    # Pattern 1: "plus X" or "+x" where X is a positive integer or float
    match = re.match(r"(?:\+\s*|plus\s+)([0-9]+(?:\.[0-9]+)?)(?=\s|$)", string)
    if match:
        return float(match.group(1))
    
    # Pattern 2: "minus X" or "-x" where X is a positive integer or float
    match = re.match(r"(?:\-\s*|minus\s+)([0-9]+(?:\.[0-9]+)?)(?=\s|$)", string)
    if match:
        return -1 * float(match.group(1))

    return None


def filter_message(message_text):
    filter_text = message_text.lower().strip()
    return filter_text


class Actioner:
    """
    Run actions based on message and react events
    """

    def __init__(self, original_message, reply_message, guild_id: int, is_bc: bool):

        self.channel = reply_message.channel
        self.guild_id = guild_id

        self.original_message = original_message.content
        self.reply_message = reply_message.content

        self.original_filtered = filter_message(self.original_message)
        self.reply_filtered = filter_message(self.reply_message)

        self.original_username = str(original_message.author)
        self.reply_username = str(reply_message.author)

        self.original_discord_id = str(original_message.author.id)
        self.reply_discord_id = str(reply_message.author.id)

        self.is_bc = is_bc

    async def action_message(self):
        if self.is_plus_two(self.reply_filtered):
            await self.run_plus_two()
            return

        if self.is_minus_two(self.reply_filtered):
            await self.run_minus_two()
            return

        if quantity := parse_arbitrary(self.reply_filtered):
            await self.run_arbitrary(quantity)

        if self.reply_filtered in zero_triggers:
            await self.channel.send('Noted...')

    
    async def action_react(self):
        pass


    def match_prompt(self, message: str, prompt: str) -> bool:
        position = message.find(prompt)
        if position == -1:
            # message doesnt contain prompt
            return False
        if position == 0:
            # prompt starts at the beginning of the message, accept this
            return True
        # prompt is later in the message, ignore
        return False
        
        

    def is_plus_two(self, message: str) -> bool:
        match = False
        for prompt in plus_two_triggers:
            match |= self.match_prompt(message, prompt)
        return match


    def is_minus_two(self, message: str) -> bool:
        match = False
        for prompt in minus_two_triggers:
            match |= self.match_prompt(message, prompt)
        return match
    

    async def run_plus_two(self):
        if self.can_give_points():
            self.record_message(2)
            await self.channel.send('Noted.')
        else:
            await self.channel.send(f"`{self.reply_username} is not in the sudoers file. This incident will be reported.`")

    async def run_minus_two(self):
        if self.can_give_points():
            self.record_message(-2)
            await self.channel.send('Noted.')
        else:
            await self.channel.send(f"`{self.reply_username} is not in the sudoers file. This incident will be reported.`")

                
    def can_give_points(self) -> bool:
        return self.original_discord_id != self.reply_discord_id
    

    def record_message(self, points: int):
        database.record_message(
                RecordMessageData(points=points, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.original_discord_id, 
                                  message_text=self.original_message,
                                  server_id=self.guild_id))

    
    async def run_arbitrary(self, quantity: float):
        sarcasm = [
            "it'll be a cold day in hell before i allow your stupid-ass FLOATS into my leaderboard, you conniving weasel",
            f"oh look, {self.reply_username} thinks they're being cute by trying to give non-integer amounts of points. how pathetic.",
            f"{quantity}? really? you're lucky i dont -2 your ass for trying that shit",
            f"is this the fucking world we live in? where discord addicts dont even have the BACKBONE to use whole numbers of points. god.",
            f"trust me buddy. just round it up. you don't need to equivocate. {int(ceil(quantity))} would have done just fine.",
            f"howabout no. that better be the last time i see a decimal point or YOU'LL BE SORRY. I KNOW WHERE YOU LIVE.",
            f"try all you want, i am NOT moving us off of the Abby-Squash System. You say 'fractional reserve pointing', i hear 'confidently incorrect simpleton'",
            f"INTEGERS ONLY. who do you think i am? a 5th grader??? decimals aren't real math. go take a calculus class and tell me how many decimals you see.",
            f"Decimals are not valid input for this opreation. Upset about it? Too bad. That's life, buddy. Maybe file a complaint with the hospital at which you were born."
        ]

        whatever = [
            "I'll allow it, but I prefer you give +2 or -2. I might not always be so kind.",
            "I'll allow it, but I prefer you give +2 or -2. I might not always be so kind.",
            "...whatever, fine.",
            "I'll allow it, but next time, please use +2 or -2.",
            "I'll allow it, but just this once.",
            "I'll allow it, but only because I'm in a good mood.",
            "I'll allow it, but only because I feel bad for you.",
            "Look. Boss doesn't like me giving points that aren't + 2 or -2. But I'll make an exception for you.",
            "Fine. But you're on thin ice, buddy.",
            "*siiiigh*  Noted.",
            "*siiiiiiiiiiiigh*  Noted.",
            "*glares at you* Don't play with me.",
            "Ok.",
            "ok.",
        ]
        

        if not quantity.is_integer():
            choice = random.choice(sarcasm)
            await self.channel.send(choice)
            return

        quantity = int(quantity)

        if quantity > 6 or quantity < -6:
            await self.channel.send('Hey. Not too much.')
            return
        
        database.record_message(
                RecordMessageData(points=quantity, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.original_discord_id, 
                                  message_text=self.original_message,
                                  server_id=self.guild_id))

        if random.random() > 0.9 and self.is_bc:
            await self.channel.send(special_hexdump(random.choice(hexdumps)))
            return
        
        if random.random() > 0.5:
            await self.channel.send(random.choice(whatever))
            return
        
        if random.random() > 0.6 and quantity > 0:
            await self.channel.send("You know what? Sure! Why not! +1 for you too.")
            database.record_message(
                RecordMessageData(points=1, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.reply_discord_id, 
                                  message_text='',
                                  server_id=self.guild_id))
            return
        
        if random.random() > 0.5:
            database.record_message(
                RecordMessageData(points=-1, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.reply_discord_id, 
                                  message_text='',
                                  server_id=self.guild_id))
            await self.channel.send("I'll allow it, but since it wasn't +2 or -2, It's gonna cost ya. -1 point.")
            return
        
        await self.channel.send("I'll allow it, but since it wasn't +2 or -2, It's gonna cost ya. -2 points.")

        database.record_message(
                RecordMessageData(points=-2, 
                                  points_giver=self.reply_discord_id, 
                                  points_receiver=self.reply_discord_id, 
                                  message_text='',
                                  server_id=self.guild_id))


        

