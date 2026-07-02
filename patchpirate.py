import requests
from halo import Halo
from colorama import Fore, init
from datetime import datetime
import hashlib
from dotenv import dotenv_values

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

            BY: ┳┓  ┏┓┓ ┏┓  ┏┓•  ┏┓┓
                ┣┫┏┓┃┫┃┏ ┫┏┓┃┃┓┓┏ ┫┃
                ┻┛┛ ┗┛┛┗┗┛┛┗┣┛┗┛┗┗┛┗ Version: 1.2.0
-----------------------------------------------------------------
"""

# Display program banner at top
print(f"{Fore.RED}{banner}")

# Check for a personal access token for higher rate limits
config = dotenv_values("config.env")
if config.get("GITHUB_TOKEN"):
    GITHUB_TOKEN = config["GITHUB_TOKEN"]
else:
    print(f"{Fore.RED}[WARN]{Fore.RESET}: {Fore.YELLOW}You are using PatchPirate without a GitHub Personal Access Token, this will work for smaller profiles without rate limiting but\nI highly reccomend that you consider adding your PAT to the config.env file.")
    print(f"{Fore.YELLOW}Your current rate limit is set to 60 requests/hour\n")
    GITHUB_TOKEN = None


HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

# Fetch all commits authored by the user across their repositories
def get_user_commits(username):
    commits = []
    repos = []

    # Fetch all repositories for the user
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 403:
        handle_rate_limit(response)
    elif response.status_code != 200:
        raise Exception(f"Error fetching repos: {response.status_code}")
    repos = response.json()
    


    print(f"{Fore.BLUE}Found {len(repos)} repositories for user {Fore.RED}{username}{Fore.BLUE}.")
    working_indicator.start()
    for repo in repos:
        repo_name = repo['name']
        owner = repo['owner']['login']


        # Fetch commits for the repository
        url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?author={username}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 403:
            handle_rate_limit(response)
        elif response.status_code != 200:
            print(f"{Fore.RED}Error fetching commits for {repo['name']}: {response.status_code}")
        data = response.json()
        for commit in data:
            commits.append({
                'repo': repo_name,
                'message': commit['commit']['message'],
                'url': commit['html_url'],
                'date': commit['commit']['author']['date'],
                'sha': commit['sha'][:7],
                'email': commit['commit']['author']['email']
            })
    working_indicator.stop()
    return commits

def get_user_profile(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 403:
        handle_rate_limit(response)
    elif response.status_code != 200:
        raise Exception(f"Error fetching profile: {response.status_code}")
    return response.json()
    
    
# Handle GitHub rate limiting errors
def handle_rate_limit(response):
    reset_timestamp = int(response.headers.get('X-RateLimit-Reset', 0))
    reset_time = datetime.fromtimestamp(reset_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    remaining = response.headers.get('X-RateLimit-Remaining', '0')
    print(f"\n{Fore.RED}GitHub API rate limit exceeded.")
    print(f"{Fore.YELLOW}Remaining requests: {remaining}")
    print(f"{Fore.YELLOW}Rate limit resets at: {Fore.CYAN}{reset_time}")
    raise Exception("Rate limit hit. Please wait for cooldown or use a personal access token.")

if __name__ == "__main__":
    username = input(f"{Fore.GREEN}Enter GitHub username: ").strip()
    profile = get_user_profile(username)
    email_addresses = set()
    obfuscated = ""
    
    try:
        user_commits = get_user_commits(username)
        for commit in user_commits:
            email = commit['email']
            if email:
                if email.endswith("noreply.github.com"):
                    obfuscated = email
                else:
                    email_addresses.add(email)

        print(f"{Fore.BLUE}Total commits found: {Fore.RED}{len(user_commits)}")
        print("---------------------------------------------------------------------")
        print(f"Obfucated noreply address: {Fore.GREEN}{obfuscated}")
        print("---------------------------------------------------------------------")
        print(f"{Fore.RED}Email Addresses:\n")
        for email in email_addresses:
            print(f"{Fore.GREEN}{email}")
        print("---------------------------------------------------------------------")
        print(f"{Fore.RED}Profile images:\n")
        for email in email_addresses:
            print(f"{Fore.GREEN}https://unavatar.io/{email}")
        print(f"{Fore.GREEN}{profile['avatar_url']}")  
            

    


    except Exception as e:
        print(f"An error occurred: {e}")
