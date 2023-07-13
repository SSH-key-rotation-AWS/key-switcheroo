import requests

# Constants
BASE_URL = "https://api.github.com"
OWNER = "SSH-key-rotation-AWS"
REPO = "team-henrique"
TOKEN = "Team_Henrique"
CURRENT_TAG = get_latest_tag() 

def get_latest_tag():
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/tags"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tags = response.json()
        latest_tag = tags[0]["name"]  # Get the latest tag name
        return latest_tag
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def get_latest_commit_sha():
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/commits"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commits = response.json()
        return commits[0]["sha"]  # Get the latest commit SHA
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def create_tag(tag_name, commit_sha):
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/git/refs"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {
        "ref": f"refs/tags/{tag_name}",
        "sha": commit_sha
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 201:
        tag = response.json()
        print(f"Tag '{tag_name}' created successfully.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Increment the tag version
version_parts = CURRENT_TAG.split(".")
major, minor, patch = int(version_parts[0][1:]), int(version_parts[1]), int(version_parts[2])
new_tag_name = f"v{major}.{minor}.{patch + 1}"

# Get the latest commit SHA
commit_sha = get_latest_commit_sha()

# Create the new tag
create_tag(new_tag_name, commit_sha)