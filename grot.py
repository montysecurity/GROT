import requests
import json
import hashlib
import os
from time import sleep
import subprocess

archive_files = False # Parses git log for every repo and collects every verion of all files ever committed
collect_authors = True # Parses git log for author names/email addresses
unique_authors = True # If true, then only display each author name once
include_forks = True # Set to true if you want to include repos the target had forked from somewhere else
download_avatar = False # Download the github profile picture

github_api_base_url = "https://api.github.com/"
username = "montysecurity"
all_authors = []

def get_user_info(url):
    userdictionary = {}
    userinfo = requests.get(url=url)
    j = json.loads(userinfo.text)
    for i in j:
        if i in [ "login", "avatar_url", "repos_url", "name", "company", "blog", "location", "email", "bio", "twitter_username", "created_at", "updated_at"]:
            userdictionary.update({i: j[i]})
    return userdictionary

def get_avatar(url):
    avatar = requests.get(url=url)
    if avatar.status_code != 200:
        print("Could not retrive avatar at " + url)
    with open("avatar.png", "wb") as f:
        for block in avatar.iter_content(1024):
            if not block:
                break
            f.write(block)
    with open("avatar.png", "rb") as f:
        bytes = f.read()
        sha256 = hashlib.sha256(bytes).hexdigest()
    print()
    print("hash for avatar is " + str(sha256))
    print("stored as avatar.png")

def get_repos(url):
    repos = requests.get(url)
    #print(repos.text)
    return repos

def parse_repos(repos):
    repos = json.loads(repos.text)
    for i in repos:
        fork = i["fork"]
        if not include_forks and fork:
            continue
        download_and_extract_repo_data(i["name"], i["html_url"], i["default_branch"])
    return repos

def download_and_extract_repo_data(name, url, restore_branch):
    if collect_authors or archive_files:
        os.system("git clone " + str(url))
    else:
        return
    if collect_authors:
        try:
            os.chdir(name)
        except FileNotFoundError:
            return
        authors = list(str(os.popen('powershell.exe "git log | findstr Author: | sort -u"').read()).split("Author: "))
        for a in authors:
            a = a.strip()
            a += f" ------ {str(name)}"
            all_authors.append(a.strip())
    if archive_files:
        powershell= f"$restore_branch = \"{str(restore_branch)}\";"
        powershell += f"New-Item -Path ../ -Name {str(name).strip()}_GROT_Hashes -ItemType 'directory';"
        powershell += """$commits=(git log | Select-String 'commit [a-z0-9]{40}'); $hashes=$(foreach ($commit in $commits) { -split $commit | Select-String '[a-z0-9]{40}' }); foreach ($hash in $hashes) {  git checkout $hash; Compress-Archive -Path ."""
        powershell += f" -DestinationPath ../{str(name).strip()}_GROT_Hashes/$hash.zip;"
        powershell += "sleep 3 }; git checkout $restore_branch"
        subprocess.run(["powershell.exe", str(powershell)])
    sleep(3)
    os.chdir("../")

userdictionary = get_user_info(github_api_base_url + "users/" + username)
if download_avatar:
    get_avatar(userdictionary["avatar_url"])
repos = get_repos(userdictionary["repos_url"])
parse_repos(repos)

print()
print()

last_author = ""
for mapping in sorted(all_authors):
    try:
        author = str(mapping).split(" ------ ")[0]
    except IndexError:
        continue
    try:
        repo = str(mapping).split(" ------ ")[1]
    except IndexError:
        continue
    if unique_authors:
        if last_author == author:
            continue
    print(f"{author}: {repo}")
    last_author = author