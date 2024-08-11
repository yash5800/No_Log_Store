from flask import Flask, render_template, request, session, send_file
from git_repo import *
from sql_operations import *
from io import BytesIO
import mimetypes
import os
import time
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Track the last request time and ping count
last_request_time = time.time()
ping_count = 0  # Initialize ping count

@app.route('/')
def main():
    global last_request_time
    last_request_time = time.time()
    return render_template('key.html')

@app.route('/check_shit', methods=['POST', 'GET'])
def check_shit():
    global last_request_time
    last_request_time = time.time()

    session['username'] = request.form['key']
    print(session['username'])
    
    data = retrive(session['username'])
    if data == 'new':
        return render_template('index.html', user=session['username'])
    
    return render_template('index.html', user=session['username'], data=data)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global last_request_time
    last_request_time = time.time()

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
    global last_request_time
    last_request_time = time.time()

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
    global last_request_time
    last_request_time = time.time()

    file_name = request.form["file_name"]
    result = delete_file(session['username'], file_name)
    
    if result:
        return render_template('index.html', status='Removed', user=session['username'], data=retrive(session['username']))
    
    return render_template('index.html', status='Unable to Remove', user=session['username'], data=retrive(session['username']))

def self_ping():
    """Pings the main endpoint to keep the service alive."""
    global ping_count
    try:
        response = requests.get('https://no-log-store.onrender.com/')
        if response.status_code == 200:
            ping_count += 1  # Increment the ping count
            print(f"Self-ping successful. Ping Count: {ping_count}")
        else:
            print("Self-ping failed with status code:", response.status_code)
    except requests.RequestException as e:
        print(f"Error during self-ping: {e}")

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=self_ping, trigger="interval", minutes=1)  # Adjust to less than 15 minutes
    scheduler.start()

    try:
        app.run()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
