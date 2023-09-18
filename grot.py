import requests
import json
import hashlib
import os
from time import sleep
import subprocess
import argparse
import shutil

parser = argparse.ArgumentParser(description="Program Description.")
parser.add_argument("-u", "--username", type=str, help="GitHub username to investigate", required=True)
parser.add_argument("-i", "--investigation", type=str, help="Name of directory to make and store result (default: results)", default="results")
parser.add_argument("-p", "--picture", action="store_true", help="Download & Calculate SHA256 for Profile picture")
parser.add_argument("-f", "--files", action="store_true", help="Iterate through commits of all accessible repos and archive files from each commit")
parser.add_argument("-a", "--authors", action="store_true", help="Display unique list of all authors from accessible repos")
parser.add_argument("-e", "--exclude-noreply", action="store_true", help="Exclude emails contains 'users.noreply.github.com' from author enumeration")
parser.add_argument("-k", "--include-forks", action="store_true", help="Also search repos this user has forked")

args = parser.parse_args()
username = args.username
investigation = args.investigation
picture = args.picture
files = args.files
authors = args.authors
exclude_github_noreply_addr = args.exclude_noreply
include_forks = args.include_forks

github_api_base_url = "https://api.github.com/"
all_authors = set()

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
    print("-------------------------- USER PPROFILE PHOTO INFO -----------------------")
    print("[+] SHA256: " + str(sha256))
    print("[+] Saved as: " + str(investigation) + "/avatar.png")
    print()

def get_repos(url):
    repos = requests.get(url)
    return repos

def parse_repos(repos):
    repos = json.loads(repos.text)
    for i in repos:
        fork = i["fork"]
        if not include_forks and fork:
            continue
        if authors or files:
            download_and_extract_repo_data(i["name"], i["html_url"], i["default_branch"])
    return repos

def download_and_extract_repo_data(name, url, restore_branch):
    print(f"[+] Cloning {name}")
    cmd = ["git", "clone", f"{str(url)}"]
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    if authors:
        try:
            os.chdir(name)
        except FileNotFoundError:
            return
        authors_list = list(str(os.popen('powershell.exe "git log | findstr Author: | sort -u"').read()).split("Author: "))
        for author in authors_list:
            if len(author) != 0:
                all_authors.add(author.strip())
    if files:
        try:
            os.chdir(name)
        except FileNotFoundError:
            return
        powershell= f"$restore_branch = \"{str(restore_branch)}\";"
        powershell += f"New-Item -Path . -Name {str(name).strip()}_GROT_Hashes -ItemType 'directory';"
        powershell += """$commits=(git log | Select-String 'commit [a-z0-9]{40}'); $hashes=$(foreach ($commit in $commits) { -split $commit | Select-String '[a-z0-9]{40}' }); foreach ($hash in $hashes) {  git checkout $hash; Compress-Archive -Path ."""
        powershell += f" -DestinationPath {str(name).strip()}_GROT_Hashes/$hash.zip;"
        powershell += "sleep 3 }; git checkout $restore_branch"
        subprocess.run(["powershell.exe", str(powershell)])
    sleep(3)

def print_authors():
    if authors:
        print("\n--------------------------- AUTHORS ----------------------")
    for author in sorted(all_authors):
        if exclude_github_noreply_addr:
            if "users.noreply.github.com" in author:
                continue
        print(f"[+] {author}")

def main():
    try:
        os.mkdir(investigation)
    except FileExistsError:
        shutil.rmtree(investigation)
        sleep(1)
        os.mkdir(investigation)
        sleep(1)
    os.chdir(investigation)
    userdictionary = get_user_info(github_api_base_url + "users/" + username)
    if picture:
        get_avatar(userdictionary["avatar_url"])
    repos = get_repos(userdictionary["repos_url"])
    parse_repos(repos)
    f = open(log_file, "a")
    print("-------------------------- USER GITHUB INFO -----------------------")
    for k in userdictionary:
        print(f"[+] {k}: {userdictionary[k]}")
    if authors:
        print_authors()
        print()

main()