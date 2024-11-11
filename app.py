from flask import Flask, render_template, request, session, send_file,send_from_directory
from git_repo import *
from sql_operations import *
from io import BytesIO
import mimetypes
import os
import requests
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route('/')
def main():
    return render_template('key.html')


@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('static', 'ads.txt')


@app.route('/check_shit', methods=['POST', 'GET'])
def check_shit():
    session['username'] = request.form['key']
    print(session['username'])
    
    data = retrive(session['username'])
    if data == 'new':
        return render_template('index.html', user=session['username'])
    
    return render_template('index.html', user=session['username'], data=data)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'username' in session:
        print("Session username:", session['username'])
    else:
        print("No username in session")
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part in the form!'
        
        file = request.files['file']
        
        if file.filename == '':
            return 'No selected file!'
        
        # Check the file size (100MB = 100 * 1024 * 1024 bytes)
        file_size = len(file.read())
        file.seek(0)  # Reset file pointer after reading size

        if file_size > 100 * 1024 * 1024:
            return 'File exceeds the maximum allowed size of 100MB!'
        
        file_content = file.read()
        file_name = file.filename
        success, file_name = upload_to_github(file_content, file_name)

        print("File upload success:", success)
        
        if success:
            insert(session['username'], file_name)
            return render_template('index.html', status='uploaded', user=session['username'], data=retrive(session['username']))
        else:
            return render_template('index.html', status='Not uploaded/File Name Already exists', user=session['username'], data=retrive(session['username']))

@app.route('/download', methods=['GET', 'POST'])
def download_file():
    if request.method == 'POST':
        file_name = request.form.get("file_name")  # Safely get file name
        if not file_name:
            return render_template('index.html', status='No file name provided', user=session.get('username'), data=retrive(session.get('username')))

        print("Entered to download file:", file_name)
        file_url = f"https://raw.githubusercontent.com/yash5800/ND_store/master/{file_name}"

        try:
            # Headers to force a fresh request (disable caching)
            headers = {
                'Cache-Control': 'no-cache',  # Prevent cached responses
                'Pragma': 'no-cache',         # Prevent cached responses
            }

            # Make the request to GitHub raw content URL without the Authorization header (for public files)
            response = requests.get(file_url, headers=headers)

            # Check for any errors in the response
            response.raise_for_status()  # Will raise an HTTPError for 4xx/5xx responses

            # Debugging: Print the final URL and headers
            print(f"Response URL: {response.url}")
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")

            # If the request was successful, process the file
            filename = os.path.basename(file_url)  # Extract file name from URL
            mime_type, _ = mimetypes.guess_type(filename)  # Guess MIME type based on file extension

            if mime_type is None:
                mime_type = 'application/octet-stream'  # Default MIME type for unknown files

            # Create an in-memory file
            file_content = BytesIO(response.content)

            # Return the file for download
            return send_file(file_content, mimetype=mime_type, as_attachment=True, download_name=filename)

        except requests.exceptions.RequestException as e:
            # Catch all request-related errors and print the response for debugging
            print(f"Error fetching file: {e}")
            if response:
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Text: {response.text}")  # Print the content of the response for further inspection
            return render_template('index.html', status=f'Error: {e}', user=session.get('username'), data=retrive(session.get('username')))

    return render_template('index.html', user=session.get('username'), data=retrive(session.get('username')))

    

@app.route('/view', methods=['GET', 'POST'])
def view():
    file_name = request.form["file_name"]
    file_url = f"https://raw.githubusercontent.com/yash5800/ND_store/master/{file_name}"
    
    response = requests.get(file_url)

    if response.status_code == 200:
        # Save the PDF temporarily
        temp_pdf_path = 'temp_pdf.pdf'
        with open(temp_pdf_path, 'wb') as f:
            f.write(response.content)
        return render_template('view_pdf.html', pdf_path=temp_pdf_path)
    else:
        return "Failed to retrieve the PDF."

@app.route('/display/<path:pdf_path>')
def display_pdf(pdf_path):
    return send_file(pdf_path, as_attachment=False)


@app.route('/fuck_off', methods=['GET', 'POST'])
def fuck_off():
    file_name = request.form["file_name"]
    result = delete_file(session['username'], file_name)
    
    
    if result:
        
        result = delete_from_github(file_name)
        
        if result:
            return render_template('index.html', status='Removed', user=session['username'], data=retrive(session['username']))
    
    return render_template('index.html', status='Unable to Remove', user=session['username'], data=retrive(session['username']))


if __name__ == '__main__':
        app.run()
