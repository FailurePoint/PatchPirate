import requests
import re
import time
from halo import Halo
from colorama import Fore, init
from datetime import datetime

# Initialize colorama with auto reset
init(autoreset=True)

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
                ┻┛┛ ┗┛┛┗┗┛┛┗┣┛┗┛┗┗┛┗ Version: 1.0.0
-----------------------------------------------------------------
"""

# Display program banner at top
print(f"{Fore.RED}{banner}")

# Optionally use a personal access token for higher rate limits
GITHUB_TOKEN = input(f"{Fore.YELLOW}Enter GitHub Personal Access Token (or press Enter to skip): ").strip()
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'} if GITHUB_TOKEN else {}

# Fetch all commits authored by the user across their repositories
def get_user_commits(username):
    commits = []
    repos = []

    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
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

    for repo in repos:
        repo_name = repo['name']
        owner = repo['owner']['login']
        print(f"{Fore.LIGHTBLACK_EX}Checking commits in repository: {repo_name}")
        
        page = 1
        while True:
            url = f"https://api.github.com/repos/{owner}/{repo_name}/commits?author={username}&page={page}&per_page=100"
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 403:
                handle_rate_limit(response)
            elif response.status_code != 200:
                print(f"Error fetching commits from {repo_name}: {response.status_code}")
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
    return commits

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
    email_addresses = set()
    obfuscated = ""
    try:
        user_commits = get_user_commits(username)
        print(f"\n{Fore.BLUE}Total commits found: {Fore.RED}{len(user_commits)}")
        print("---------------------------------------------------------------------")

        for commit in user_commits:
            email = commit['email']
            if email:
                if email.endswith("noreply.github.com"):
                    obfuscated = email
                else:
                    email_addresses.add(email)
        print(f"\nObfucated noreply address: {Fore.GREEN}{obfuscated}")
        print("Email addresses found:")
        for email in email_addresses:
            print(f"{Fore.GREEN}{email}")

    except Exception as e:
        print(f"An error occurred: {e}")
