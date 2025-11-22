## ScoreBot for discord

### Setup

```
pip install discord.py python-dotenv
```

Make a file named .env in the root directory of the project, contents as follows. This is gitignored.

```
DISCORD_BOT_TOKEN="your-token-here"
```

You can find your token on the discord developer portal page for your bot account, after registering it.

To initialize the sqlite database, run

```
python setup_db.py up
```
Then run the bot with

```
python main.py
```

### Functionality

???
