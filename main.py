from utils import *
import requests
import pydriller as pdl
import re
import time

'''
I'll try two different approaches:

- Search directly from API, and filter data
    - For this I loose some tools from pydrilles, but not restricted for projects
    - Is restricted to only 30 answers
- Download repos using Pydrilles and filtering
    - For this I need a list of projects
'''

#repo = download_repo("apache", "echarts", 'projetcts')

owner = 'apache'
projects = ['dubbo']

projects_download_list = []

file = open('key.txt', 'r')
token = file.readlines()[0]
file.close()

'''for p in projects:
    download_issues(owner=owner,
                    project=p,
                    key='code',
                    token=token)
    if flag:
        path = f'projects/{owner}_{p}/repo'
        os.mkdir(path)
        download_repo(owner,p,path)
        extract_comments(path)'''
path = 'projects/'

'''file = open('key.txt', 'r')
token = file.readlines()[0]
file.close()

extract_survival_time(owner, 'dubbo', token)'''

'''data = {}
for p in projects:
    types = analyze_commits(path=path,
                            owner=owner,
                            project=p)
    data[p] = types


build_stacked_bar(data)'''

check = check_issues_solved_by_commits(owner='apache', project='dubbo')

print(check)
#extract_commits(path='projects/apache_dubbo',key = 'smell', owner='apache',project='dubbo')

#Join all projects toghether