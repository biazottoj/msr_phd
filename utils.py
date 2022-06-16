import json
from git import Repo
import requests
import os
import requests
import pydriller as pdl
import csv
import time
import re

#Function for download a repository
def download_repo(user, project, dst_path):
    ghurl = f'https://github.com/{user}/{project}'

    try:
        if len(os.listdir(dst_path)) == 0:
            print(f'Cloning {user}/{project}')
            Repo.clone_from(ghurl, dst_path)
    except:
        print(f'ERROR: {user}/{project}')

#Filter commits messages from a repository
def filter_commits(key, repo, branch_name):
    commits = list(repo.iter_commits(branch_name))
    filtered_commits = []
    for c in commits:
        if key.lower() in c.message.lower():
            filtered_commits.append(c)
    return filtered_commits

#Using Github API to search commits (by message) with keywords
def search_commits(key):
    return requests.get(url=f'https://api.github.com/search/commits?q={key}').json()

#Using Github API to search issues (by titile) with keywords
def search_issues(key):
    return requests.get(url=f'https://api.github.com/search/issues?q={key}').json()

#Modeling commits data so export a CSV
def model_commits_data(key):
    commits = search_commits(key)
    data = []
    for i, c in enumerate(commits['items']):
        if i == 0:
            print(c)
        data.append(['commit',
                         'GIT',
                         c['repository']['full_name'] if not None else 'null',
                         c['html_url'] if not None else 'null',
                         c['commit']['message'] if not None else 'null',
                         c['author']['login'] if not None else 'null',
                         c['commit']['author']['email'] if not None else 'null',
                         c['commit']['author']['date'] if not None else 'null'])
    return data

#Modeling issues data so export a CSV
def model_issues_data(key):
    issues = search_issues(key)
    data = []
    for i, c in enumerate(issues['items']):
        if i == 0:
            print(c['repository_url'])
        #TechDebt: try to extract from data later
        repo = get_issue_repo(c['repository_url'])
        email = 'awsome.email@superb.domain.nl'
        #email = get_issue_author_email(m['user']['url']) [READY BUT NOT TESTED]

        data.append(['issue',
                         'GIT',
                         repo,
                         c['html_url'] if c['html_url'] != None else 'null',
                         c['title'] if c['title'] != None else 'null',
                         c['user']['login'] if c['user'] != None else 'null',
                         email,
                         c['created_at'] if c['created_at'] != None else 'null'])

        for m in get_issue_messages(c['comments_url']):
            if key in m['body']:
                #email = get_issue_author_email(m['user']['url'])
                email = 'awsome.email@superb.domain.nl'
                data.append(['issue_comment',
                             'GIT',
                             repo,
                             c['html_url'] if not None else 'null',
                             m['body'] if not None else 'null',
                             m['user']['login'] if not None else 'null',
                             email,
                             m['created_at'] if not None else 'null'])
    return data

#Recovering repo name for issues
def get_issue_repo(link:str):
    key = [key for key, item in enumerate(link) if item == '/']
    return link[(key[4]+1):]

def get_issue_messages(link):
    return requests.get(link).json()

def get_issue_author_email(link):
    return requests.get(link).json()['email']

#Function to write data to a CSV file
def write_database(key:str):
    headers = ['source', 'platform', 'project', 'uid', 'content','author','email',  'date']
    rows = model_commits_data(key)
    rows.extend(model_issues_data(key))
    with open('csv/database.csv', 'w', encoding='UTF8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)
        file.close()
    with open('projetcts/projetcs.txt', 'w') as file:
        wr = []
        for r in rows:
            wr.append(f'{r[2]}\n')
        file.writelines(set(wr))
        file.close()

#Function to recover the comments of a issue
def download_issues_comments(link, n_comments, key):
    n_pages = int(n_comments / 100)

    if n_comments > (n_pages * 100) or n_pages == 0:
        n_pages += 1
    flag = False

    comments_list = []

    #As we have a limite of 100 results per requeste, we have to go through each page to recover the results 100 by 100;
    for i in range(n_pages):
        headers = {"accept": "application/vnd.github.v3+json",
                   "u": "biazottoj:token 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"}
        comments_list = requests.get(f"{link}"
                                f"?sort=created"
                                f"&direction=desc"
                                f"&per_page=100"
                                f"&page={i + 1}",
                                headers=headers).json()
        for comment in comments_list:
            if key in comment['body']:
                comment['key_in_comment'] = True
                flag = True
            else:
                comment['key_in_comment'] = False
        #As we have a limit of 1000 requests/hour, the system wait 4 seconds after each request.
        time.sleep(4)
    
    return comments_list, flag

def store_comments(comments_list, issue_number, path):
    for i,comment in enumerate(comments_list):
        with open(f"{path}/issue_{issue_number}_comment_{i}.json", "w") as file:
            json.dump(comment, file)

def download_issues(owner, project, key):
    #n_issues = get_issue_count(owner,project) ## Get all issues from a repo
    n_issues = get_issue_search_count(owner, project, key) # Get the issues from a repo considering the key

    if n_issues > 0:
        n_pages = int(n_issues/100)

        if 'projects' not in os.listdir():
            os.mkdir('projects')
        path = f'projects/{owner}_{project}'
        os.mkdir(path)
        path = path + '/issues'
        os.mkdir(path)

        if n_issues > (n_pages * 100) or n_pages == 0:
            n_pages += 1

        for i in range(n_pages):
            print(f'Downloading page {i+1}/{n_pages}')
            headers = {"accept": "application/vnd.github.v3+json",
                       "u": "biazottoj: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"}
            issues_list = requests.get(f'https://api.github.com/search/issues?'
                                       f'q={key}'
                                       f'+type:issue'
                                       f'+repo:{owner}/{project}'
                                       f'+sort:author-date-asc'
                                       f'&per_page=100'
                                       f'&page={i+1}',
                                       headers=headers).json()['items']
            for issue in issues_list:

                flag = False
                comments=[]

                if issue['comments'] > 0:
                    comments, flag = download_issues_comments(link = issue['comments_url'],
                                                              key = key,
                                                              n_comments=issue['comments'])
                key_in_title = key in issue['title']
                key_in_body = key in issue['body']

                if flag or key_in_title or key_in_body:
                    with open(f"{path}/issue_{issue['number']}.json", "w") as file:
                        issue['key_in_body'] = key_in_body
                        issue['key_in_title'] = key_in_title
                        issue['key_in_comments'] = flag
                        json.dump(issue, file)

                    store_comments(comments_list=comments,
                                   issue_number=issue['number'],
                                   path=path)

            time.sleep(4)
            n_files = len(os.listdir(path))
        return True
    else:
        return False

def get_issue_count(owner, project):
    headers = {"accept": "application/vnd.github.v3+json",
               "Authorization": "token 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"}
    issues = requests.get(f"https://api.github.com/search/issues?q=repo:{owner}/{project}+type:issue",
                          headers=headers).json()

    return issues['total_count']

def get_issue_search_count(owner, project, key):
    headers = {"accept": "application/vnd.github.v3+json",
               "u": "biazottoj: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"}
    issues_list = requests.get(f'https://api.github.com/search/issues?'
                               f'q={key}'
                               f'+type:issue'
                               f'+repo:{owner}/{project}',
                               headers=headers).json()
    return issues_list['total_count']


def extract_comments(path, key, ower, project):
    repo = pdl.Repository(f'{path}/repo')
    os.mkdir(f'{path}/commits')
    for i, c in enumerate(repo.traverse_commits()):
        close_issue = re.search("[a-zA-Z] #\d", c.msg)
        has_key = key in c.msg
        data = {}
        if close_issue or has_key:
            if close_issue:
                if has_key:
                    data['operation'] = 'b'
                else:
                    data['operation'] = 'i'
            else:
                data['operation'] = 'k'

            data['project'] = f'{ower}/{project}'
            data['modified_files'] = len(c.modified_files)
            data['loc_diff'] = c.lines
            data['sha'] = c.hash
            data['author'] = c.author.email
            data['author_date'] = str(c.author_date)
            data['commit_date'] = str(c.committer_date)

            with open(f'{path}/commits/commit_{c.hash}.json', 'w') as file:
                json.dump(data,file)

