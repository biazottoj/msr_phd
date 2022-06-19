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

build_stacked_bar({"dubbo":analyze_commits('projects', 'apache', 'dubbo')})