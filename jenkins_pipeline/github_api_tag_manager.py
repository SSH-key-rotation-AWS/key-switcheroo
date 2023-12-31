import os
import requests
import re

# import boto3
# from botocore.exceptions import ClientError

# Constants
BASE_URL = "https://api.github.com"
OWNER = "SSH-key-rotation-AWS"
REPO = "key-switcheroo"

def get_latest_tag(token: str, timeout: int = 10) -> str:
    """Gets the latest tag from github so it can increment by one"""
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/tags"
    # Uses github PAT token for access
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.Timeout as exc:
        print(f"The API call to {url} timed out after {timeout} seconds.")
        raise requests.Timeout from exc
    if response.status_code == 200:
        tags = response.json()
        # Get the latest tag name
        latest_tag = tags[0]["name"]
        print(f"Latest tag is {latest_tag}")
        return latest_tag
    print(f"Error while getting latest tag: {response.status_code} - {response.text}")
    return ""


def bump_tag(token: str, old_tag: str):
    # Get the latest commit SHA
    commit_sha = get_latest_commit_sha(token)
    # Increment the tag version
    version_parts = old_tag.split(".")
    major, minor, patch = (
        int(version_parts[0]),
        int(version_parts[1]),
        int(version_parts[2]),
    )
    new_tag_name = f"{major}.{minor}.{patch + 1}"
    # Create the new tag
    create_tag(token, new_tag_name, commit_sha)


def get_latest_commit_sha(token: str, timeout: int = 10) -> str:
    """Retrieves the latest commit sha which is needed for the Github API to get the latest tag"""
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/commits"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.Timeout as exc:
        print(f"The API call to {url} timed out after {timeout} seconds.")
        raise requests.Timeout from exc
    if response.status_code == 200:
        commits = response.json()
        # Get the latest commit SHA
        return commits[0]["sha"]
    raise RuntimeError(
        f"Error while fetching latest commit sha: {response.status_code} - {response.text}. \
        Token is f{token}"
    )


def create_tag(token: str, tag_name: str, commit_sha: str, timeout: int = 10):
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/git/refs"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"ref": f"refs/tags/{tag_name}", "sha": commit_sha}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
    except requests.Timeout as exc:
        print(f"The API call to {url} timed out after {timeout} seconds.")
        raise requests.Timeout from exc
    if response.status_code == 201:
        print(f"Tag '{tag_name}' created successfully.")
    else:
        print(f"Error while creating new tag: {response.status_code} - {response.text}")

if __name__=="__main__":
    unprocessed_token = os.environ["GITHUB_PAT"]
    processed_token = re.sub('\s+',' ', unprocessed_token).strip()
    current_tag = get_latest_tag(processed_token)
    bump_tag(token=processed_token, old_tag=current_tag)
