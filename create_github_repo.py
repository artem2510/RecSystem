"""Create a GitHub repository and upload the current project files without requiring git.

Usage:
  Set the GITHUB_TOKEN environment variable first.
  python create_github_repo.py --name RecSystem --description "My RecSystem project" --private false

The script will:
  1. Create the repository under your GitHub account.
  2. Upload all files from the current directory, excluding venvs and ignored paths.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

IGNORED_DIRS = {"venv", "backend/.venv", "backend/venv", "frontend/node_modules", ".git"}
IGNORED_FILES = {"create_github_repo.py"}


def request_json(url, data=None, headers=None, method="GET"):
    headers = headers or {}
    headers["Accept"] = "application/vnd.github+json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API error {exc.code}: {body}") from exc


def get_github_username(token):
    url = "https://api.github.com/user"
    data = request_json(url, headers={"Authorization": f"Bearer {token}"})
    return data["login"]


def create_repo(token, name, description, private):
    url = "https://api.github.com/user/repos"
    payload = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": False,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    return request_json(url, data=data, headers=headers, method="POST")


def upload_file(token, owner, repo, path, content_bytes, message):
    path_quoted = "/".join(urllib.parse.quote(part) for part in path.replace("\\", "/").split("/"))
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path_quoted}"
    encoded = base64.b64encode(content_bytes).decode("utf-8")
    payload = {
        "message": message,
        "content": encoded,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    return request_json(url, data=data, headers=headers, method="PUT")


def should_ignore(relpath):
    if relpath in IGNORED_FILES:
        return True
    for ignored in IGNORED_DIRS:
        if relpath == ignored or relpath.startswith(ignored + os.sep):
            return True
    return False


def collect_files(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""
        if should_ignore(rel_dir):
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if not should_ignore(os.path.join(rel_dir, d))]
        for filename in filenames:
            relpath = os.path.join(rel_dir, filename) if rel_dir else filename
            if should_ignore(relpath):
                continue
            files.append(relpath)
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="Create a GitHub repo and upload project files.")
    parser.add_argument("--name", required=True, help="GitHub repository name")
    parser.add_argument("--description", default="", help="Repository description")
    parser.add_argument("--private", default="false", choices=["true", "false"], help="Create a private repository")
    parser.add_argument("--repo", help="Use an existing repository (owner/repo) instead of creating a new one")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: Set the GITHUB_TOKEN environment variable with a GitHub personal access token.")
        sys.exit(1)

    if args.repo:
        owner_repo = args.repo.strip()
        if "/" not in owner_repo:
            print("Error: --repo must be in the form owner/repo")
            sys.exit(1)
        owner, repo = owner_repo.split("/", 1)
    else:
        owner = get_github_username(token)
        repo_data = create_repo(token, args.name, args.description, args.private == "true")
        repo = repo_data["name"]
        print(f"Created repository: {repo_data['html_url']}")

    root = os.path.abspath(os.path.dirname(__file__))
    files = collect_files(root)
    print(f"Uploading {len(files)} files...")
    for path in files:
        with open(os.path.join(root, path), "rb") as fd:
            content_bytes = fd.read()
        message = f"Add {path}"
        upload_file(token, owner, repo, path, content_bytes, message)
        print(f"Uploaded: {path}")

    print(f"Upload complete. Repository available at https://github.com/{owner}/{repo}")


if __name__ == "__main__":
    main()
