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
    file_name = request.form["file_name"]
    print("entered to download file:", file_name)
    file_url = f"https://raw.githubusercontent.com/yash5800/ND_store/master/{file_name}"
    try:
        response = requests.get(file_url)
        response.raise_for_status()
            
        filename = os.path.basename(file_url)
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = 'application/octet-stream'
            
        file_content = BytesIO(response.content)
        return send_file(file_content, mimetype=mime_type, as_attachment=True, download_name=filename)
        
    except requests.RequestException as e:
        print(f"Error fetching file: {e}")
        return render_template('index.html', status='Unable to Download', user=session['username'], data=retrive(session['username']))

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
