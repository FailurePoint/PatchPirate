import requests
import hashlib
import urllib.request
import urllib.error
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
                ┻┛┛ ┗┛┛┗┗┛┛┗┣┛┗┛┗┗┛┗ Version: 1.2.3
                
“The secret of creativity is knowing how to discover and exploit your sources.” ― Prof.Salam Al Shereida 
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

    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=10000"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 403:
            handle_rate_limit(response)
        elif response.status_code != 200:
            raise Exception(f"Error fetching repos: {response.status_code}")
        data = response.json()
        if not data:
            break
        repos.extend(data)
        page += 1

    print(f"{Fore.BLUE}Found {len(repos)} repositories for user {Fore.RED}{username}{Fore.BLUE}.")

    working_indicator.start()
    for repo in repos:
        repo_name = repo['name']
        owner = repo['owner']['login']

        page = 1
        while True:
            url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?author={username}&page={page}&per_page=10000"
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 403:
                handle_rate_limit(response)
            elif response.status_code != 200:
                break
            data = response.json()
            if not data:
                break
            for commit in data:
                commits.append({
                    'repo': repo_name,
                    'message': commit['commit']['message'],
                    'url': commit['html_url'],
                    'date': commit['commit']['author']['date'],
                    'sha': commit['sha'][:7],
                    'email': commit['commit']['author']['email']
                })
            page += 1
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

def get_gravatar_url(email):
    email = email.strip().lower()
    hash_ = hashlib.sha256(email.encode()).hexdigest()
    url = f"https://api.gravatar.com/v3/profiles/{hash_}?d=404"
    try:
        urllib.request.urlopen(url)
        response = requests.get(url)
        return response.json()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            None
        else:
            return "Error fetching Gravatar profile:"

if __name__ == "__main__":
    username = input(f"{Fore.GREEN}Enter GitHub username: ").strip()
    if config["DISABLE_PROFILE_INFO"] == "False":
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
        if config["DISABLE_PROFILE_INFO"] == "False":
            print("---------------------------------------------------------------------")
            print(f"{Fore.RED}Account Details:\n")
            print(f"{Fore.GREEN}Username:{Fore.RESET} {profile['login']}")
            print(f"{Fore.GREEN}Name:{Fore.RESET} {profile.get('name', 'N/A')}")
            print(f"{Fore.GREEN}Bio: {Fore.RESET}{profile['bio'].replace('\n', '') if profile['bio'] is not None else 'None'}")
            print(f"{Fore.GREEN}Location:{Fore.RESET} {profile.get('location', 'N/A')}")
            print(f"{Fore.GREEN}Company:{Fore.RESET} {profile.get('company', 'N/A')}")
            print(f"{Fore.GREEN}Public Email:{Fore.RESET} {profile.get('email', 'N/A')}")
            print(f"{Fore.GREEN}X Profile:{Fore.RESET} {profile.get('twitter_username', 'N/A')}")
            print(f"{Fore.GREEN}Blog:{Fore.RESET} {profile.get('blog', 'N/A')}")
            print(f"{Fore.GREEN}Followers:{Fore.RESET} {profile.get('followers', 'N/A')}")
            print(f"{Fore.GREEN}Following:{Fore.RESET} {profile.get('following', 'N/A')}")
            print(f"{Fore.GREEN}Account Created:{Fore.RESET} {profile['created_at']}")
            print(f"{Fore.GREEN}Last Updated:{Fore.RESET} {profile['updated_at']}\n")
        print("---------------------------------------------------------------------")
        print(f"{Fore.RED}Discovered Email Addresses:\n")
        print(f"Obfucated noreply address: {Fore.GREEN}{obfuscated}\n")
        for email in email_addresses:
            print(f"{Fore.GREEN}{email}")
        if config["DISABLE_LOOKUPS"] == "False":
            print("---------------------------------------------------------------------")
            print(f"{Fore.RED}Profile images:\n")
            for email in email_addresses:
                print(f"{Fore.GREEN}https://unavatar.io/{email}")
            for email in email_addresses:
                gravatar_url = get_gravatar_url(email)
                if gravatar_url is not None:
                    print(f"{Fore.GREEN}{gravatar_url['profile_url']}")
            print(f"{Fore.GREEN}{profile['avatar_url']}")
        
            

    


    except Exception as e:
        print(f"An error occurred: {e}")
