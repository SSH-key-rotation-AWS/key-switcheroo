import requests
import boto3 
from botocore.exceptions import ClientError

# Constants
BASE_URL = "https://api.github.com"
OWNER = "SSH-key-rotation-AWS"
REPO = "team-henrique"
CURRENT_TAG = ""


def get_secret():

    secret_name = "key-switcheroo_github_pat"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as failed_secrets_api_call:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise failed_secrets_api_call

    # Decrypts secret using the associated KMS key.
    RETURNTOKEN = get_secret_value_response['SecretString']
    return RETURNTOKEN

def get_latest_tag(timeout=10) -> str:
    '''Gets the latest tag from github so it can increment by one'''
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/tags"
    # Uses github PAT token for access
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.Timeout:
        print(f"The API call to {url} timed out after {timeout} seconds.")
    if response.status_code == 200:
        tags = response.json()
        # Get the latest tag name
        latest_tag = tags[0]["name"]
        return latest_tag
    print(f"Error: {response.status_code} - {response.text}")
    return ""

def bump_tag():
    # Get the latest commit SHA
    commit_sha = get_latest_commit_sha()
    # Increment the tag version 
    version_parts = CURRENT_TAG.split(".")
    major, minor, patch = int(version_parts[0]), int(version_parts[1]), int(version_parts[2])
    new_tag_name = f"{major}.{minor}.{patch + 1}"
    # Create the new tag
    create_tag(new_tag_name, commit_sha)

def get_latest_commit_sha(timeout=10):
    '''Retrieves the latest commit sha which is needed for the Github API to get the latest tag'''
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/commits"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.Timeout:
        print(f"The API call to {url} timed out after {timeout} seconds.")
    if response.status_code == 200:
        commits = response.json()
        # Get the latest commit SHA
        return commits[0]["sha"]
    print(f"Error: {response.status_code} - {response.text}")
    return None

def create_tag(tag_name, commit_sha, timeout=10):
    url = f"{BASE_URL}/repos/{OWNER}/{REPO}/git/refs"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    payload = {
        "ref": f"refs/tags/{tag_name}",
        "sha": commit_sha
    }
    try:
        response = requests.get(url, headers=headers, json=payload, timeout=timeout)
    except requests.Timeout:
        print(f"The API call to {url} timed out after {timeout} seconds.")
    if response.status_code == 201:
        print(f"Tag '{tag_name}' created successfully.")
    else:
        print(f"Error: {response.status_code} - {response.text}")

TOKEN = get_secret()
CURRENT_TAG = get_latest_tag()
bump_tag()
