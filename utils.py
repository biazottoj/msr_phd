from git import Repo
import requests
import os
import requests
import pydriller
import csv

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

        data.append(['issue',
                         'GIT',
                         repo,
                         c['html_url'] if c['html_url'] != None else 'null',
                         c['title'] if c['title'] != None else 'null',
                         c['user']['login'] if c['user'] != None else 'null',
                         'awsome.email@superb.domain.nl',
                         c['created_at'] if c['created_at'] != None else 'null'])

        for m in get_issue_messages(c['comments_url']):
            if key in m['body']:
                data.append(['issue_comment',
                             'GIT',
                             repo,
                             c['html_url'] if not None else 'null',
                             m['body'] if not None else 'null',
                             m['user']['login'] if not None else 'null',
                             'awsome.email@superb.domain.nl',
                             m['created_at'] if not None else 'null'])
    return data

#Recovering repo name for issues
def get_issue_repo(link:str):
    key = [key for key, item in enumerate(link) if item == '/']
    return link[(key[4]+1):]

def get_issue_messages(link):
    return requests.get(link).json()

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