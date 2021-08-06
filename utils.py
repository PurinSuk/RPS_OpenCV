import random
from choiceClass import Choice

def bot_choice():
    return Choice(random.randint(0, 2))

def bot_vs_player(player, bot):
    # Case 1: player loses
    if (player is Choice.rock and bot is Choice.paper) or \
        (player is Choice.paper and bot is Choice.scissors) or \
        (player is Choice.scissors and bot is Choice.rock):
        return -1
    # Case 2: player wins
    elif (player is Choice.rock and bot is Choice.scissors) or \
        (player is Choice.paper and bot is Choice.rock) or \
        (player is Choice.scissors and bot is Choice.paper):
        return 1
    # Case 3: draw
    else:
        return 0

def image_path(choice):
    if choice is None:
        return "none.jpg"
    elif choice is Choice.rock:
        return "rock_rps.png"
    elif choice is Choice.paper:
        return "paper_rps.png"
    else:
        return "scissors_rps.png"