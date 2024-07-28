import requests
import json
import base64
encoded_string = "Z2l0aHViX3BhdF8xMUEzQklQU1kwcUh5b3pWUmprYThZX3BFaGl0WlFTaVhwN3FOOERLbjgxbUVwYzdLdG92VFZQN083eUM1dHRRMWhTWVFBUFZLTkF6UmVUaDc5"
decoded_bytes = base64.b64decode(encoded_string)
decoded_string = decoded_bytes.decode('utf-8')


# Replace with your GitHub username, repository name, and access token
username = 'yash5800'
repository = 'ND_store'
access_token = decoded_string
commit_message = 'Add file via Flask'

print(f"my key:{access_token}")


# Function to upload file content to GitHub
def upload_to_github(file_content, file_name):
    print(f"my key:{access_token}")
    print("Entered")
    base_url = f'https://api.github.com/repos/{username}/{repository}/contents/'
    headers = {'Authorization': f'token {access_token}'}
    
    # Encode file content to base64
    encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    # Check if the file already exists
    response = requests.get(base_url + file_name, headers=headers)
    
    if response.status_code == 200:
        # File exists, need to update it
        sha = response.json()['sha']
        payload = {
            'message': 'adding file',
            'content': encoded_content,
            'sha': sha,
            'branch': 'main'
        }
    elif response.status_code == 404:
        # File does not exist, create it
        payload = {
            'message': commit_message,
            'content': encoded_content,
            'branch': 'main'
        }
    else:
        # Handle other potential errors
        print(f"Error checking file existence: {response.status_code} - {response.text}")
        return False
    
    # Convert payload to JSON
    payload = json.dumps(payload)
    
    # Make PUT request to create/update file
    response = requests.put(base_url + file_name, headers=headers, data=payload)
    
    # Check if request was successful
    if response.status_code == 200 or response.status_code == 201:
        print("File saved successfully")
        return True
    else:
        print(f"Error saving file: {response.status_code} - {response.text}")
        return False
