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
'''for p in projects:
    flag = download_issues(owner=owner,
                    project=p,
                    key='smell')
    if flag:
        path = f'projects/{owner}_{p}/repo'
        os.mkdir(path)
        download_repo(owner,p,path)
        extract_comments(path)'''
path = 'projects/apache_dubbo'

extract_comments(path=path,
                 key='smell',
                 ower=owner,
                 project='dubbo')

