import re
import math
import database.db as database
from discord import Message
from discord import Embed
from discord_helpers import mention_user

PREFIX = "+"
COMMAND_REGEX = re.compile(r"\+(\w+)")
newline = "\n"

PAGE_SIZE = 15
ADORNATIONS = {1: " 🥇", 2: " 🥈", 3: " 🥉"}


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

        guild = message.guild

        if guild is None:
          return 
        
        chunks = message.content.split(' ')


        is_global: bool = len(chunks) > 1 and chunks[-1].lower() == 'global'

        # for page number processing, we need to remove the global text
        if is_global:
          chunks = [c for c in chunks if c != 'global']

        # figure out what page to show
        page = 1
        if len(chunks) > 1:
          try:
            page = int(chunks[1])
            if page < 1:
              page = 1
          except TypeError:
            pass

        server_id = None if is_global else guild.id

        scoreboard_count = database.get_scoreboard_count(server_id)
        num_pages = math.ceil(scoreboard_count / PAGE_SIZE)
        
        if num_pages < page:
          s = 's' if num_pages != 1 else ''
          await message.reply(f'b-b-but i only have a total of {num_pages} page{s} to show u... 🥀')
          return

        scoreboard = database.get_scoreboard(server_id, page)
    
        title = "Top mathletes in *the entire world*" if is_global else f"Top mathletes in *{guild.name}*"

        embed = Embed(title=title, color=0xC5A2F0)
        if message.guild and message.guild.icon:
            embed.set_thumbnail(url=message.guild.icon.url)

        rank_start = (page - 1) * PAGE_SIZE
        lines = [f"Viewing page {page} of {num_pages}\n"]

        for idx, row in enumerate(scoreboard):
            rank = rank_start + idx + 1
            adornation = ADORNATIONS.get(rank, "")
            lines.append(
                f"`#{rank:>2}` {mention_user(row.user_discord_id)} - **{row.total_score}** {adornation}"
            )

        lines.append("\nTo view other pages, use `+scoreboard [page_number]`")
        embed.description = "\n".join(lines)
        await message.reply(embed=embed)
