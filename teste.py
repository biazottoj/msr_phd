import re

keywords = [
'close',
'closes',
'closed',
'fix',
'fixes',
'fixed',
'resolve',
'resolves',
'resolved'
]
text = 'I had fixed #11274 in this issue #886.'

possible_issues = [re.sub("[^0-9]","",x) for x in text.split(' ') if '#' in x]

print(possible_issues)