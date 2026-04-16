import os
from discord import Client, Intents, DMChannel, TextChannel
from actioner import Actioner
from command_handler import CommandHandler
from dotenv import load_dotenv


load_dotenv()  # reads variables from a .env file and sets them in os.environ

BOT_TOKEN = os.environ['DISCORD_BOT_TOKEN']
DEBUG_THREAD_ONLY = False

SECRET_PROXY_MODE_USER_IDS = [467178363019329537, 609840104621735939]

intents = Intents.default()
intents.messages = True
intents.message_content = True

# Configure bot to require message and message content intents
class ScoreBot(Client):
    def __init__(self):
        super().__init__(intents=intents)
        
bot = ScoreBot()
command_handler = CommandHandler()


# Whenever the bot connects to a server
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to discord')

allowed_channels = ['score bot']

# Whenever the bot sees a message
@bot.event
async def on_message(data):
    if data.author == bot.user:
        return

    if isinstance(data.channel, DMChannel):
        # checks if its a DM, used for the "proxy" pass through feature
        if data.author.id in SECRET_PROXY_MODE_USER_IDS:
            # pass through!
            parts = data.content.split(' ')
            channel_name = parts[0]
            rest = ' '.join(parts[1:])

            channels = bot.get_all_channels()
            for channel in channels:
                print(channel.name)
                if channel.name == channel_name:
                    if isinstance(channel, TextChannel):
                        print(f'sending to {channel.name}: {rest}')
                        await channel.send(rest)
                    return
        return
                
    thread_or_channel_name = data.channel.name

    if DEBUG_THREAD_ONLY and thread_or_channel_name not in allowed_channels:
        print(f'Debug mode: not acting on channel: {thread_or_channel_name}')
        return

    if data.reference:
        # This is a reply, so we can check to see if there is score to add or remove
        original_message = await data.channel.fetch_message(data.reference.message_id)

        actioner = Actioner(reply_message=data, original_message=original_message)
        await actioner.action_message()
    
    else:        
        # Check to see if there is a bot command, and run it if there is
        await command_handler.handle_command(data)
    

bot.run(BOT_TOKEN)