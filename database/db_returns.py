from dataclasses import dataclass

@dataclass
class ScoreboardRow:
    """This class is returned from the db#get_scoreboard()

    Attributes:
        user_discord_id (str): The Discord ID of the row's user 
        total_score (int): The total score of that user

    """
    user_discord_id: str
    total_score: int