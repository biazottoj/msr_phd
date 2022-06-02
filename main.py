from utils import *
import requests
import pydriller as pdl

'''
I'll try two different approaches:

- Search directly from API, and filter data
    - For this I loose some tools from pydrilles, but not restricted for projects
    - Is restricted to only 30 answers
- Download repos using Pydrilles and filtering
    - For this I need a list of projects
'''



'''for issue in response['items']:
    for key,value in issue.items():
        print(f'{key}: {value}')
    print('\n---')'''

#repo = pdl.Repository(path_to_repo="https://github.com/biazottoj/SubPath_Identifier")

'''for c in repo.traverse_commits():
    print(c.author.name)'''


key = 'a div vai pro meio'
write_database(key)