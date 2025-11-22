from dataclasses import dataclass

@dataclass
class RecordMessageData:
    """This class is for passing data into the db#record_message() function

    Attributes:
        points_giver (str): The Discord ID of the user giving points (person replying)
        points_receiver (str): The Discord ID of the user receiving points
        message_text (str): The text of the message receiving points
        points (int): The number of points to award

    """
    points_giver: str
    points_receiver: str
    message_text: str
    points: int