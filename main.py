from builtins import object

from utils import *
import requests
import pydriller as pdl
import re
import time

file = open('key.txt', 'r')
token = file.readlines()[0]
file.close()

projects = {"eclipse": ['jkube'],
            "microsoft": ['typescript',
                          'vscode',
                          'wsl',
                          'microsoft-ui-xaml',
                          'pylance-release',
                          'terminal'],
            "facebook": ['jest',
                         'flow',
                         'react']}

# download_issues('apache', 'dubbo','smell', token)

# extract_survival_time('apache', 'dubbo')

# build_stacked_bar({"dubbo":analyze_commits('projects', 'apache', 'dubbo')})

# analyze_commits_modification_information('apache', 'dubbo')
# build_grouped_bar_chart(analyze_commits_modification_information('apache', 'dubbo'))
# build_bar_chart()

#search_repositories('smell', token)

#download_issues('microsoft','pylance-release','smell',token)


types = {}
for owner, p in projects.items():
    for p1 in p:
        '''download_issues(owner=owner,
                        project=p1,
                        key='smell',
                        token=token)'''
        # extract_commits(path=f'projects/{owner}_{p1}', key='smell', owner=owner, project=p1)

        # types[p1] = analyze_commits('projects', owner, p1)

        # extract_survival_time(owner, p1)

        # analyze_commits_modification_information(owner, p1)

        # print(f'{p1} -> {check_author_issue(owner, p1)}')
# build_stacked_bar(types)
