# GROT
Github Repo OSINT Tool

## Requirements

- Python 3.11+
- Windows OS
- PowerShell 5+

## Introduction

GROT is a simple little tool that can be used to mine data from a publicly accessible GitHub account via the REST API (there is no support for GitLab at the moment). Provided a username (`-u`, `--username`) it will automatically collect the bio and display that information. Optionally it can also:

1. Download and hash the profile picture
2. Iterate through every commit of every accessible repo and do the following:
    - Collect authors
    - Archive files and put in Zip file named after the commit hash
    - Search commit history and file content history for a string

## Main Use Cases

- OPSEC: check your own GitHub OPSEC
- OSINT: persona investigations
- DFIR/CTI: collect and archive malware samples

## Other Notes

- There is an option to include repos the user has forked
- There is an option to exclude no-reply addresses from the author list. It will not effect file archiving or keyword searching.

## Usage

```
usage: grot.py [-h] -u USERNAME [--userinfo] [-i INVESTIGATION] [-p] [-f] [-a] [-e] [-k] [-s SEARCH] [-r REPO] [--seconds SECONDS]

GitHub Repo OSINT Tool

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        GitHub username to investigate
  --userinfo            Print username info
  -i INVESTIGATION, --investigation INVESTIGATION
                        Name of directory to make and store result (default: results)
  -p, --picture         Download & Calculate SHA256 for Profile picture
  -f, --files           Iterate through commits of all accessible repos and archive files from each commit
  -a, --authors         Display unique list of all authors from accessible repos
  -e, --exclude-noreply
                        Exclude emails contains 'users.noreply.github.com' from author enumeration
  -k, --include-forks   Also search repos this user has forked
  -s SEARCH, --search SEARCH
                        Search for the provided string in all commits
  -r REPO, --repo REPO  Limit search to the repo provided
  --seconds SECONDS     Number of seconds to sleep between archiving commits (Default: 3) (Increase this if you see an error sayng zip files are being used by        
                        another process)
```