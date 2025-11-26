import re
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
      scoreboard = database.get_scoreboard()
      embed = Embed(title="Scoreboard", color=0xc5a2f0)

      for row in scoreboard: 
        embed.add_field(name='', value=f"{mention_user(row.user_discord_id)} — {row.total_score}", inline=False)
      
      await message.reply(embed=embed)