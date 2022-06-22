import os


issue_count = {}
for file in os.listdir("projects"):
    issues = [x for x in os.listdir(f'projects/{file}/issues') if "comment" not in x]
    issue_count[file] = len(issues)

print(issue_count)
