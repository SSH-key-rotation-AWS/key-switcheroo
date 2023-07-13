def find_latest_tag():
    url = f'https://api.github.com/repos/SSH-key-rotation-AWS/team-henrique/tags'
    response = requests.get(url, auth=(repo_owner, access_token))
    tags = response.json()
    if tags:
        latest_tag = tags[0]['name']
        return latest_tag
    else:
        return None

