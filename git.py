#!/usr/bin/env python
# coding: utf-8

# ## Import Section

# In[ ]:


import requests
import json
import subprocess
import os


# ## Functions

# In[ ]:


def create_root_directory(app_name):
    try:
        # Check the home path
        home_dir = os.path.expanduser('~')
        # Extract username
        home_user = home_dir.split('/')[-1]
        # Create a root data directory
        data_dir = f'{home_dir}/.{home_user}_data'
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        app_data_dir = f'{data_dir}/{app_name}'
        if not os.path.exists(app_data_dir):
            os.mkdir(app_data_dir)
        return {
            'Is Created': True,
            'User': home_user,
            'Home': home_dir,
            'Data Directory': data_dir,
            'App Data Directory': app_data_dir
        }
    except:
        return {'Is Created': False}


# Get the owner data
def get_owner_data(auth_token):
    req_url = "https://api.github.com/user"
    headers_list = {
        "Accept": "*/*",
        "User-Agent": "Create repo app",
        "Authorization": f"Bearer {auth_token}"
    }
    payload = ""
    response = requests.request("GET", req_url, data=payload,  headers=headers_list)
    return json.loads(response.text)


def create_github_repo(auth_token, repo_name, is_private=True):
    req_url = "https://api.github.com/user/repos"
    headers_list = {
        "Accept": "*/*",
        "User-Agent": "Create repo app",
        "Authorization": f"Bearer {auth_token}"
    }
    payload = ""
    response = requests.request("GET", req_url, data=payload,  headers=headers_list)
    if response.status_code == 200:
        git_repos = json.loads(response.text)
        # Check if the name exists
        repo_not_found = True
        for d in git_repos:
            if repo_name == d['name']:
                repo_not_found = False
        if repo_not_found:
            headers_list["Content-Type"] = "application/json"
            payload = {
                "name": repo_name,
                "private": is_private
            }
            response = requests.request("POST", req_url, data=json.dumps(payload), headers=headers_list)

            if response.status_code == 201:
                return {
                    'status': True,
                    'message': 'repo created'
                }
            else:
                return {
                    'status': False,
                    'message': 'repo creation failed'
                }
        else:
            return {
                'status': False,
                'message': 'repo exists'
            }
    else:
        return {
            'status': False,
            'message': 'github data not accessible'
        }


# Delete a GitHub repo
def delete_repo(auth_token, owner, repo_name):
    req_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    headers_list = {
        "Accept": "*/*",
        "User-Agent": "Create repo app",
        "Authorization": f"Bearer {auth_token}"
    }
    payload = ""
    response = requests.request("DELETE", req_url, data=payload,  headers=headers_list)
    status = False
    msg = ''
    if response.status_code == 204:
        status = True
        msg = 'repo deleted'
    elif response.status_code == 404:
        msg = 'repo not found'
    elif response.status_code == 403:
        msg = 'forbidden'
    else:
        msg = 'unknown'
    return {
        'status': status,
        'message': msg
    }


# Json data handler
def write_creds_v1(details, file_path):
    try:
        PASSWORD_MANAGER_VERSION = '1.0'
        headers = list(details[0].keys())
        creds = {
            'Version': PASSWORD_MANAGER_VERSION,
            'Is Encrypted': False,
            'Headers': headers,
            'Details': details,
        }
        with open(file_path, 'w') as json_file:
            json_file.write(json.dumps(creds))
        return {
            'status': True,
            'data': creds
        }
    except Exception as e:
        return {
            'status': False,
            'data': e
        }


def read_creds_v1(file_path):
    try:
        with open(file_path, 'r') as json_file:
            data = json.loads(json_file.read())
        return {
            'status': True,
            'data': data
        }
    except Exception as e:
        return {
            'status': False,
            'data': e
        }


# ## Constants

# In[ ]:


app_name = 'github_repo_creation'
root_dir = create_root_directory(app_name)
app_data_dir = root_dir['App Data Directory']
cwd = os.getcwd()


# ### Save GitHub access token inside the local machine

# In[ ]:


auth_token_file = f'{app_data_dir}/auth_token.json'
if os.path.exists(auth_token_file):
    token_data = read_creds_v1(auth_token_file)
else:
    github_auth_token = input('Enter GitHub auth token - ')
    details = [{
        'Token': github_auth_token
    }]
    token_data = write_creds_v1(details, auth_token_file)
auth_token = token_data['data']['Details'][0]['Token']


# ### Create the repo on GitHub

# In[ ]:


try:
    owner_data = get_owner_data(auth_token)
    owner_login = owner_data['login']
    owner_html_url = owner_data['html_url']
except Exception as e:
    print('repo access failed!')
    print(f'Error message:\n{e}')


# In[ ]:


# Take the new repository name
new_repo_name = input('Enter the repository name: ')
new_repo_name = new_repo_name.replace(' ', '-').lower()
# Create the repository
create_repo = create_github_repo(auth_token, new_repo_name)
# Name already exists check
while create_repo['message'] == 'repo exists':
    new_repo_name = input('The given name already exists, choose a new one - ')
    create_repo = create_github_repo(auth_token, new_repo_name)
if create_repo['status']:
    print('Repo created on GitHub successfully!')
    remote_url = f"{owner_html_url}/{new_repo_name}"
else:
    print(f"Error message: {create_repo['message']}")
    print('Repo creation failed!')


# ## Delete a repo

# In[ ]:


# delete_repo(auth_token, owner_login, 'azam-test')


# ### Create a git repo locally

# In[ ]:


git_commands = {
    'status': ['git', 'status'],
    'init': ['git', 'init'],
    'add': ['git', 'add', '.'],
    'rename branch': ['git', 'branch', '-M', 'main'],
    'add origin': ['git', 'remote', 'add', 'origin', remote_url],
    'commit': ['git', 'commit', '-m', 'initial commit'],
    'push': ['git', 'push', '-u', 'origin', 'main']
}


# In[ ]:


# Git init
try:
    subprocess.check_output(git_commands['status'])
except subprocess.CalledProcessError:
    init_check = subprocess.check_call(git_commands['init'])


# ### Create a .gitignore file locally

# In[ ]:


# Save the gitignore file locally
gitignore_file = f'{cwd}/.gitignore'
if os.path.exists(gitignore_file):
    print('gitignore file exists')
else:
    gitignore_topics = []
    t = input('Write gitignore topic or X to skip - ')
    if t.lower() != 'x':
        while t.lower() != 'q':
            gitignore_topics.append(t.strip().lower())
            t = input('Add more topic or Q to quit - ')
        gitignore_url = f"https://www.toptal.com/developers/gitignore/api/{','.join(gitignore_topics)}"
        gitignore_response = requests.get(gitignore_url)
        if gitignore_response.status_code == 200:
            with open(gitignore_file, 'w') as gitig:
                gitig.write(gitignore_response.text)
            print('gitignore file generated successfully!')
        else:
            print("Error occured while taking response from gitignore.io")
    else:
        print('No gitignore file added.')


# ### Add the files to git

# In[ ]:


add_check = subprocess.check_call(git_commands['add'])


# In[ ]:


rename_check = subprocess.check_call(git_commands['rename branch'])


# In[ ]:


origin_check = subprocess.check_call(git_commands['add origin'])
commit_check = subprocess.check_call(git_commands['commit'])
push_check = subprocess.check_call(git_commands['push'])


# In[ ]:


## FIND ANY WAY TO DESTROY A PYTHON SCRIPT AFTER A SUCCESSFUL RUN

