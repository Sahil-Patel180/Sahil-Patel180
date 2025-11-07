import requests
import os
from datetime import datetime

# Your GitHub username
USERNAME = Sahil-Patel180
README_FILE = "README.md"

def fetch_repos(username, count=5):
    url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page={count}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def update_readme(projects):
    with open(README_FILE, "r", encoding="utf-8") as f:
        readme = f.read()

    start = "<!-- PROJECTS:START -->"
    end = "<!-- PROJECTS:END -->"
    before = readme.split(start)[0]
    after = readme.split(end)[-1]

    project_md = "\n".join([f"- [{repo['name']}]({repo['html_url']}) ⭐ {repo['stargazers_count']} | Updated: {repo['updated_at'].split('T')[0]}" for repo in projects])

    new_readme = f"{before}{start}\n{project_md}\n{end}{after}"

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(new_readme)

if __name__ == "__main__":
    repos = fetch_repos(USERNAME)
    update_readme(repos)
