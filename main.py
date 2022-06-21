from utils import *
import requests
import pydriller as pdl
import re
import time

file = open('key.txt', 'r')
token = file.readlines()[0]
file.close()

#download_issues('apache', 'dubbo','smell', token)

#extract_survival_time('apache', 'dubbo')

#build_stacked_bar({"dubbo":analyze_commits('projects', 'apache', 'dubbo')})

#analyze_commits_modification_information('apache', 'dubbo')
#build_grouped_bar_chart(analyze_commits_modification_information('apache', 'dubbo'))
#build_bar_chart()

#search_repositories('smell', token)

with open('projects_list.json', 'r') as file:
    projects = json.load(file)
    types = {}
    for owner in projects.keys():
        if owner != 'project_count' and owner != 'total_issues':
            for project in projects[owner]['projects'].keys():
                #extract_survival_time(owner=owner, project=project)

                try:
                    types[f'{owner}_{project}'] = analyze_commits('projects', owner, project)
                except:
                    pass
                '''download_issues(owner=owner,
                                project=project,
                                key='smell',
                                token=token)
                extract_commits(path=f'projects/{owner}_{project}',key='smell',owner=owner,project=project)'''
    build_stacked_bar(types)