import requests
import json
from time import sleep
import os
import subprocess

username = "montysecurity"
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
    if repo_fork:
        continue
    repo_name = repo["name"]
    repo_fullname = repo["full_name"]
    repo_url = f"https://github.com/{repo_fullname}"
    print(repo_url)
    print(repo_name)
    commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
    #print(commits_url)
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
    cmd = ["git", "clone", f"{str(repo_url)}"]
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

print("[+] Listing Emails and Linked Repos")
for pair in emails:
    print("--->", pair)