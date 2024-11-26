import requests
import json
import os
import subprocess
import argparse
from sys import platform

parser = argparse.ArgumentParser(description="Extract Email Addresses from GitHub account repos. By default, only searches repos with one contributor and does not search forks.")
parser.add_argument("-u", "--username", type=str, help="GitHub Username")
parser.add_argument("-c", "--clone-repos", action="store_true", help="Clone repos locally")
parser.add_argument("-k", "--include-forks", action="store_true", help="Pull data from repos the account has forked")
parser.add_argument("-q", "--include-contributors", action="store_true", help="Pull data from repos that have multiple contributors (automatically made true if including forks)")
args = parser.parse_args()

username = args.username
clone = args.clone_repos
include_forks = args.include_forks
include_contributors = args.include_contributors

if include_forks:
    include_contributors = True

if clone:
    try:
        os.mkdir(username)
    except FileExistsError:
        os.rmdir(username)
        os.mkdir(username)
    os.chdir(username)

repos_url = f"https://api.github.com/users/{username}/repos"
emails = set()

repos = requests.get(url=repos_url)

for repo in json.loads(repos.text):
    if repos.status_code != 200:
        print(repos, repos.text)
        continue
    repo_fork = repo["fork"]
    # Skip repo if it is a fork
    if repo_fork and not include_forks:
        continue
    repo_name = repo["name"]
    repo_fullname = repo["full_name"]
    repo_url = f"https://github.com/{repo_fullname}"
    contributors_url = f"https://api.github.com/repos/{repo_fullname}/contributors"
    contributors = requests.get(url=contributors_url)
    contributors = json.loads(contributors.text)
    if len(contributors) > 1 and not include_contributors:
        continue
    if not include_contributors:
        contributer_username = contributors[0]['login']
        if contributer_username != username:
            continue
    print(f"[+] Parsing {repo_name}")
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    repo_commits = requests.get(url=commits_url)
    if repo_commits.status_code != 200:
        print(repo_commits, repo_commits.text)
        continue
    repo_commits = json.loads(repo_commits.text)
    i = 0
    for commit in repo_commits:
        repo_commit_email = commit['commit']['author']['email']
        if "@users.noreply.github.com" not in repo_commit_email:
            repo_email_pair = str(repo_name + " --- " + repo_commit_email)
            emails.add(repo_email_pair)
    if clone:
        cmd = ["git", "clone", f"{str(repo_url)}"]
        if platform in ["windows", "win32"]:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.wait()
        elif platform in ["linux", "linux2"]:
            subprocess.run(cmd)
        else:
            print(f"[!] Failed to clone repo. Unknown platform: {platform}")

print("\n[+] Listing Emails and Linked Repos")
for pair in emails:
    print("--->", pair)