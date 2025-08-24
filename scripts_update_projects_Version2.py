import os, re, sys, textwrap, requests

USERNAME = os.getenv("TARGET_USERNAME", "Sahil-Patel180")
TOKEN = os.getenv("GITHUB_TOKEN")
README_PATH = os.getenv("README_PATH", "README.md")
MAX_REPOS = int(os.getenv("MAX_REPOS", "3"))

API = "https://api.github.com"
HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}" if TOKEN else ""
}

def fetch_repos(user):
    repos = []
    page = 1
    while page < 5:  # up to 400 repos
        r = requests.get(f"{API}/users/{user}/repos",
                         params={"per_page": 100, "page": page, "sort": "updated", "direction": "desc"},
                         headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"GitHub API error ({r.status_code}): {r.text}", file=sys.stderr)
            break
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return repos

def infer_stack(repo):
    topics = repo.get("topics") or []
    lang = repo.get("language") or ""
    stack_bits = []
    lang_map = {
        "Jupyter Notebook": "Python (Notebook)",
        "Python": "Python",
        "HTML": "HTML",
        "JavaScript": "JS",
        "TypeScript": "TS",
        "R": "R",
        "SQL": "SQL"
    }
    if lang:
        stack_bits.append(lang_map.get(lang, lang))
    for t in topics:
        if t.lower() in {"power-bi","powerbi"} and "Power BI" not in stack_bits:
            stack_bits.append("Power BI")
        if t.lower() in {"ml","machine-learning"} and "ML" not in stack_bits:
            stack_bits.append("ML")
        if t.lower() in {"dashboard"} and "Dashboard" not in stack_bits:
            stack_bits.append("Dashboard")
        if t.lower() in {"excel"} and "Excel" not in stack_bits:
            stack_bits.append("Excel")
    return " · ".join(stack_bits) if stack_bits else "Data / Analytics"

def concise(desc, width=70):
    if not desc:
        return "Project description coming soon."
    d = " ".join(desc.strip().split())
    return (d[:width-3] + "...") if len(d) > width else d

def main():
    if not os.path.isfile(README_PATH):
        print(f"README not found at {README_PATH}", file=sys.stderr)
        sys.exit(0)

    repos = fetch_repos(USERNAME)
    # Filter out forks, archived, profile repo
    filtered = [
        r for r in repos
        if not r.get("fork")
        and not r.get("archived")
        and r.get("name") != USERNAME
    ]
    # Sort by pushed_at descending (already mostly sorted) but ensure
    filtered.sort(key=lambda r: r.get("pushed_at", ""), reverse=True)
    top = filtered[:MAX_REPOS]

    if not top:
        table = "| Project | Stack | Summary |\n|--------|-------|---------|\n| _No repositories found_ | - | - |"
    else:
        rows = []
        for r in top:
            name = r.get("name")
            html_url = r.get("html_url")
            stack = infer_stack(r)
            desc = concise(r.get("description"))
            rows.append(f"| <a href=\"{html_url}\"><strong>{name}</strong></a> | {stack} | {desc} |")
        table = "| Project | Stack | Summary |\n|--------|-------|---------|\n" + "\n".join(rows)

    with open(README_PATH, encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- AUTO-PROJECT-START -->"
    end_marker = "<!-- AUTO-PROJECT-END -->"
    pattern = re.compile(
        rf"({re.escape(start_marker)})(.*)({re.escape(end_marker)})",
        re.DOTALL
    )

    replacement_inner = (
        f"{start_marker}\n"
        f"<!-- This section is auto-updated by .github/workflows/auto-projects.yml -->\n"
        f"{table}\n"
        f"{end_marker}"
    )

    if not pattern.search(content):
        print("Markers not found. No update performed.", file=sys.stderr)
        sys.exit(0)

    new_content = pattern.sub(replacement_inner, content)

    if new_content == content:
        print("No changes detected.")
        return

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("README updated with latest repositories.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Script error: {e}", file=sys.stderr)
        sys.exit(0)