import json
from git import Repo
import os
import requests
import pydriller as pdl
import csv
import time
import re
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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

# =================================== New tasks ===========================

#Function to recover the total of issues that contains a keyword in a repo
def get_issue_search_count(owner, project, key, token):
    headers = {"accept": "application/vnd.github.v3+json",
               "authorization": f"token {token}"}
    issues_list = requests.get(f'https://api.github.com/search/issues?'
                               f'q={key}'
                               f'+type:issue'
                               f'+repo:{owner}/{project}',
                               headers=headers).json()
    time.sleep(4)
    return issues_list['total_count']

#Function to recover the comments of an issue
def download_issues_comments(link, n_comments, key, token):
    n_pages = int(n_comments / 100)
    if n_comments > (n_pages * 100) or n_pages == 0:
        n_pages += 1
    flag = False
    comments_list = []
    #As we have a limite of 100 results per requeste, we have to go through each page to recover the results 100 by 100;
    for i in range(n_pages):
        headers = {"accept": "application/vnd.github.v3+json",
                   "authorization": f"token {token}"}
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

#Function to save each issue comment in a json file
def store_comments(comments_list, issue_number, path):
    for i,comment in enumerate(comments_list):
        with open(f"{path}/issue_{issue_number}_comment_{i}.json", "w") as file:
            json.dump(comment, file)

#Function to recover the hash of the commit that closed an issue
def find_commit_close_issue(url, token):
    headers = {"accept": "application/vnd.github.v3+json",
               "authorization": f"token {token}"}
    events = requests.get(url).json()
    return [x['commit_id'] for x in events if x['event'] == 'closed']

#Function to donwload issues
def download_issues(owner, project, key, token):
    #n_issues = get_issue_count(owner,project) ## Get all issues from a repo
    n_issues = get_issue_search_count(owner, project, key, token) # Get the issues from a repo considering the key
    if n_issues > 0:
        n_pages = int(n_issues/100)
        if n_issues > (n_pages * 100) or n_pages == 0:
            n_pages += 1
        path = f'projects/{owner}_{project}'
        if 'projects' not in os.listdir():
            os.mkdir('projects')
        if f'{owner}_{project}' not in os.listdir('projects'):
            os.mkdir(path)
        if 'issues' in os.listdir(path):
            os.rmdir(f'{path}/issues')
        path = path + '/issues'
        os.mkdir(path)
        for i in range(n_pages):
            print(f'Downloading page {i+1}/{n_pages}')
            headers = {"accept": "application/vnd.github.v3+json",
                       "authorization": f"token {token}"}
            issues_list = requests.get(f'https://api.github.com/search/issues?'
                                       f'q={key}'
                                       f'+type:issue'
                                       f'+repo:{owner}/{project}'
                                       f'+sort:author-date-asc'
                                       f'&per_page=100'
                                       f'&page={i+1}',
                                       headers=headers).json()['items']
            time.sleep(4)
            for i in issues_list:
                issue = requests.get(i['url'], headers=headers).json()
                flag = False
                comments=[]
                if issue['comments'] > 0:
                    comments, flag = download_issues_comments(link = issue['comments_url'],
                                                              key = key,
                                                              n_comments=issue['comments'],
                                                              token=token)
                key_in_title = key in issue['title']
                key_in_body = key in issue['body']
                if flag or key_in_title or key_in_body:
                    with open(f"{path}/issue_{issue['number']}.json", "w") as file:
                        issue['key_in_body'] = key_in_body
                        issue['key_in_title'] = key_in_title
                        issue['key_in_comments'] = flag
                        if (issue['state'] == 'closed'):
                            commit = find_commit_close_issue(issue['events_url'], token)[0]
                        else:
                            commit = 'null'
                        issue['commit'] = commit
                        json.dump(issue, file)
                    store_comments(comments_list=comments,
                                   issue_number=issue['number'],
                                   path=path)
            #time.sleep(4)
    else:
        print(f'None issue was found with the keyword "{key}"!')

def extract_commits(path, key, owner, project):
    repo = pdl.Repository(f'{path}/repo')
    os.mkdir(f'{path}/commits')
    keywords = ['fix',
                'fixes',
                'fixed',
                'close',
                'closes',
                'closed',
                'resolve',
                'resolves',
                'resolved']
    for i, c in enumerate(repo.traverse_commits()):
        close_issue = any(re.search(f'{keyword}[\s:]#\d.', c.msg) for keyword in keywords)
        has_key = key in c.msg
        data = {}
        if close_issue or has_key:
            if close_issue:
                if has_key:
                    data['operation'] = 'Both'
                else:
                    data['operation'] = 'Issue'
            else:
                data['operation'] = 'Key'
            data['project'] = f'{owner}/{project}'
            data['message'] = c.msg
            data['modified_files'] = len(c.modified_files)
            data['loc_diff'] = c.lines
            data['sha'] = c.hash
            data['author'] = c.author.email
            data['author_date'] = str(c.author_date)
            data['commit_date'] = str(c.committer_date)
            with open(f'{path}/commits/commit_{c.hash}.json', 'w') as file:
                json.dump(data,file)

#============== Analysis Functions ==============
def analyze_commits(path, owner, project):
    extract_path = f'{path}/{owner}_{project}/commits'
    types = []
    for commit in os.listdir(extract_path):
        with open(f'{extract_path}/{commit}', 'r') as file:
            types.append(json.load(file)['operation'])
    return types

def extract_survival_time(owner, project):
    path = f'projects/{owner}_{project}/issues'
    list = os.listdir(path)
    filtered_issues = [f for f in list if 'comment' not in f]
    survival_times = []
    for f in filtered_issues:
        with open(f'{path}/{f}') as file:
            j = json.load(file)
            status = j['state']
            if status == 'closed':
                open_date = datetime.strptime(j['created_at'].replace('T', ' ').replace('Z',''),'%Y-%m-%d %H:%M:%S')
                close_date = datetime.strptime(j['closed_at'].replace('T', ' ').replace('Z',''),'%Y-%m-%d %H:%M:%S')
                survival_times.append((close_date - open_date).days)
    print(survival_times)
    build_box_plot(title="Issues survival time", data = survival_times)

def check_author_issue(owner, project):
    issue_list = {}
    for issue in [x for x in os.listdir(f'projects/{owner}_{project}/issues') if 'comment' not in x]:
        with open(f'projects/{owner}_{project}/issues/{issue}', 'r') as issue_file:
            issue_json = json.load(issue_file)
            if issue_json['state'] == 'closed' and issue_json['commit'] != 'null':
                '''
                Pydriller do not extract the author login. So, to do not make other request to Github API,
                I checked if the author and the closer was the same into the issue. However, I just considered
                issues that were closed by commits.
                '''
                issue_list[issue_json['number']] = True if issue_json['user']['login'] == issue_json['closed_by']['login'] else False
    return issue_list


def analyze_commits_modification_information(owner, project):
    path = f'projects/{owner}_{project}/commits'
    project = []
    commits = []
    loc = []
    files = []
    for commit in os.listdir(path):
        with open(f'{path}/{commit}', 'r') as file:
            c = json.load(file)
            project.append(c['project'])
            commits.append(c['sha'])
            loc.append(c['loc_diff'])
            files.append(c['modified_files'])

    df = pd.DataFrame({
        "project":project,
        "commit": commits,
        "loc": loc,
        "files": files
    })
    df.set_index('project', inplace=True)

    return df.groupby(['project']).mean()

#======= Plot Functions ===============
def build_box_plot(title, data, x='', y=''):
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_title(title)
    plt.boxplot(data)
    plt.ylabel(y)
    plt.xlabel(x)
    plt.show()

def build_stacked_bar(data = {}):
    project = []
    type = []
    for k in data.keys():
        for d in data[k]:
            project.append(k)
            type.append(d)
    rawData = {'project':project, 'type':type}
    df = pd.DataFrame(rawData)
    df.set_index(df['project'],inplace=True)
    cross = pd.crosstab(index=df['project'],
                        columns=df['type'],
                        normalize="index")
    cross_count = pd.crosstab(index=df['project'],
                        columns=df['type'])
    cross.plot(kind='bar',
               stacked = True,
               colormap = 'tab20c',
               figsize=(8,4),
               rot=0,
               width = 1)
    plt.legend(loc="lower right", ncol=len(set(df['type'])))
    plt.ylabel("Proportion")
    plt.xlabel("")
    plt.title("Proportion of commit's objective")
    for n, x in enumerate([*cross.index.values]):
        for (proportion, y_loc, count) in zip(cross.loc[x], cross.loc[x].cumsum(), cross_count.loc[x]):
            if proportion > 0:
                plt.text(x=n - 0.22,
                         y = (y_loc - proportion) + (proportion / 2),
                         s=f'{round(proportion*100,1)}%',
                         color="black",
                         fontsize=8,
                         fontweight="bold")
    plt.show()

def build_bar_chart():
    data = analyze_commits_modification_information('apache', 'dubbo')

    courses = list(data.index)
    values = list(data['loc'].values)

    fig = plt.figure(figsize=(10, 5))

    # creating the bar plot
    plt.bar(courses, values, color='maroon',
            width=0.4)

    plt.xlabel("Courses offered")
    plt.ylabel("No. of students enrolled")
    plt.title("Students enrolled in different courses")
    plt.show()



