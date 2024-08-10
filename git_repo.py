import requests
import json
import base64
import os
import time


# Replace with your GitHub username, repository name, and access token
username = os.getenv('USER')
repository = os.getenv('REPO')
access_token = os.getenv('MY_API')
commit_message = 'Add file via Flask'

print(f"my key:{access_token}")

def upload_to_github(file_content, file_name):
    base_url = f'https://api.github.com/repos/{username}/{repository}/contents/'
    headers = {'Authorization': f'token {access_token}'}
    file_name = file_name.replace(" ", "")
    # Check if the file already exists
    response = requests.get(base_url + file_name, headers=headers)
    
    if response.status_code == 200:
        # File exists, modify the file name by appending a timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        file_name = f"{timestamp}_{file_name}"
        print(f"File with the same name exists. Renamed to {file_name}")
    
    # Now proceed with the chunked upload as before
    CHUNK_SIZE = 1 * 1024 * 1024  # 1 MB chunks
    chunks = [file_content[i:i + CHUNK_SIZE] for i in range(0, len(file_content), CHUNK_SIZE)]
    sha = None

    for i, chunk in enumerate(chunks):
        encoded_content = base64.b64encode(chunk).decode('utf-8')
        payload = {
            'message': f'Adding chunk {i+1} of {len(chunks)}',
            'content': encoded_content,
            'branch': 'main'
        }

        if sha:
            payload['sha'] = sha  # Include SHA to continue the file upload

        payload = json.dumps(payload)
        retries = 0
        success = False

        while retries < 3:  # Simple retry mechanism
            try:
                response = requests.put(base_url + file_name, headers=headers, data=payload, timeout=30)
                if response.status_code in [200, 201]:
                    sha = response.json().get('content', {}).get('sha')
                    print(f"Chunk {i+1} uploaded successfully")
                    success = True
                    break
                else:
                    print(f"Error uploading chunk {i+1}: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error during chunk upload {i+1}: {e}")
            
            retries += 1
            print(f"Retrying chunk {i+1} upload ({retries}/3)")

        if not success:
            return False  # Exit if a chunk fails to upload after 3 attempts

    return True,file_name

