from utils import *
import requests
import pydriller as pdl
import re

'''
I'll try two different approaches:

- Search directly from API, and filter data
    - For this I loose some tools from pydrilles, but not restricted for projects
    - Is restricted to only 30 answers
- Download repos using Pydrilles and filtering
    - For this I need a list of projects
'''

#repo = download_repo("apache", "echarts", 'projetcts')

download_issues(owner='apache',
                project='dubbo',
                key='smell')

