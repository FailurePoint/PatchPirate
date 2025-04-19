from colorama import Fore, init # Copywrite (c) 2013-2025, Jonathan Hartley (https://github.com/tartley)
from halo import Halo # Copywrite (c) 2016-2025, Singh
import patchpirate # Copywrite (c) 2025, Gratonic (https://github.com/Gratonic)
import json
import os

# Initialize colorama with auto reset
init(autoreset=True)

# Initialize loading indicator
working_indicator = Halo(text=f'Searching user commits...', spinner='pong')

# program banner
banner = r"""
 ______                  _     ______ _                         
(_____ \        _       | |   (_____ (_)              _         
 _____) )____ _| |_ ____| |__  _____) )  ____ _____ _| |_ _____ 
|  ____(____ (_   _) ___)  _ \|  ____/ |/ ___|____ (_   _) ___ |
| |    / ___ | | |( (___| | | | |    | | |   / ___ | | |_| ____|
|_|    \_____|  \__)____)_| |_|_|    |_|_|   \_____|  \__)_____)

   BY: ┳┓  ┏┓┓ ┏┓  ┏┓•  ┏┓┓     ┏┓         • 
       ┣┫┏┓┃┫┃┏ ┫┏┓┃┃┓┓┏ ┫┃     ┃┓┏┓┏┓╋┏┓┏┓┓┏
       ┻┛┛ ┗┛┛┗┗┛┛┗┣┛┗┛┗┗┛┗ and ┗┛┛ ┗┻┗┗┛┛┗┗┗  Version: 1.0.1   
-----------------------------------------------------------------
"""

# display program banner at top of the terminal
print(f"{Fore.RED}{banner}")

def clear_data_dir():
    username = input(f"{Fore.GREEN}Enter GitHub username: ").strip()
    GITHUB_TOKEN = input(f"{Fore.YELLOW}Enter GitHub Personal Access Token (or press Enter to skip): ").strip()
    user_input = {
        "username": username, 
        "github_token": GITHUB_TOKEN
    }

def collect_user_input():
    pass

def get_user_commits():
    pass

def analysis_and_display_output():
    pass