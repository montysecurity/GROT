# GROT
Github Repo OSINT Tool

## Introduction

GROT can be used by CTI/OSINT analysts to extract email addresses belonging to contributors of repos under a given GitHub account. By default, it only searches repos where the account in question was the only contributor and the tool ignores emails containing `@users.noreply.github.com`.

It can also be used to search repos that have more than one contributor or have been forked. If you want to clone the repos, that can be done with the `-c, --clone-repos` flag. This can be useful if the repo/user may be deleted in the future and its contents needs to be preserved for further analysis.

## Latest Changes

- Works on both Windows and Linux
- Simplified parameters

## Usage

```
usage: grot.py [-h] [-u USERNAME] [-c] [-k] [-q]

Extract Email Addresses from GitHub account repos. By default, only searches repos with one contributor and does not search forks.

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        GitHub Username
  -c, --clone-repos     Clone repos locally
  -k, --include-forks   Pull data from repos the account has forked
  -q, --include-contributors
                        Pull data from repos that have multiple contributors (automatically made true if including forks)
```