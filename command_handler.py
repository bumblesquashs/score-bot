import re
import math
import database.db as database
from discord import Message
from discord import Embed
from discord_helpers import mention_user

PREFIX = "+"
COMMAND_REGEX = re.compile(r'\+(\w+)')
newline = "\n"

class CommandHandler:
    """
    Handle different commands
    """

    async def handle_command(self, message: Message) -> None:
      message_content = message.content

      # print(f"Message content: {message_content}")

      if not message_content.startswith(PREFIX):
         return
      
      command_name_match = COMMAND_REGEX.search(message_content)

      print(f"Regex match: {command_name_match}")

      if not command_name_match:
         return

      match command_name_match.group(1):
        case "ping":
            await self.pong(message)
        case "scoreboard":
            await self.scoreboard(message)
        case _:
          pass
         
    async def pong(self, message: Message):
      await message.reply("Pong!")

    async def scoreboard(self, message: Message):
      chunks = message.content.split(' ')
      page = 1
      if len(chunks) > 1:
        try:
          page = int(chunks[1])
          if page < 1:
             page = 1
        except TypeError:
          pass

      scoreboard_count = database.get_scoreboard_count()
      num_pages = math.ceil(scoreboard_count / 15)
      
      if num_pages < page:
         s = 's' if num_pages != 1 else ''
         await message.reply(f'b-b-but i only have a total of {num_pages} page{s} to show u... 🥀')
         return

      scoreboard = database.get_scoreboard(page)
   

      embed = Embed(title="Scoreboard", color=0xc5a2f0)
      embed.add_field(name='', value=f"Viewing page {page} of {num_pages}")

      for idx, row in enumerate(scoreboard): 
        adornation = ''
        if page == 1:
          if idx == 0:
              adornation = ' 🥇'
          elif idx == 1:
              adornation = ' 🥈'
          elif idx == 2:
              adornation = ' 🥉'
        embed.add_field(name='', value=f"{mention_user(row.user_discord_id)} — {row.total_score}{adornation}", inline=False)
      
      embed.add_field(name='', value=f"To view other pages, use +scoreboard [page_number]")
      await message.reply(embed=embed)
