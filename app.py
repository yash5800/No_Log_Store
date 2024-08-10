from flask import Flask,render_template,url_for,request,g,redirect,session,send_file
from git_repo import *
from sql_operations import *
from io import BytesIO
import mimetypes
import os

app = Flask(__name__)

app.secret_key = "1101"

@app.route('/')
def main():
    return render_template('key.html')

@app.route('/check_shit',methods=['POST','GET'])
def check_shit():
    session['username'] = request.form['key']
    print(session['username'])
    
    data = retrive(session['username'])
    if data == 'new':
        return render_template('index.html',user=session['username'])
    
    return render_template('index.html',user=session['username'],data=data)

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
        
        file_content = file.read()
        file_name = file.filename
        success,file_name = upload_to_github(file_content, file_name)

        print("File upload success:", success)
       
        
        if success:
            insert(session['username'], file_name)
            return render_template('index.html', status='uploaded', user=session['username'], data=retrive(session['username']))
        else:
            return render_template('index.html', status='Not uploaded/File Name Already exists', user=session['username'], data=retrive(session['username']))

@app.route('/download' , methods=['GET', 'POST'])
def download_file():
    file_name = request.form["file_name"]
    print("entered to download file : ", file_name)
    file_url = f"https://raw.githubusercontent.com/yash5800/ND_store/master/{file_name}"
    try:
            response = requests.get(file_url)
            response.raise_for_status()  # Ensure we notice bad responses
            
            # Extract filename from URL or provide a default name
            filename = os.path.basename(file_url)
            
            # Determine MIME type based on file extension
            mime_type, _ = mimetypes.guess_type(filename)
            if mime_type is None:
                mime_type = 'application/octet-stream'  # Default MIME type
            
            file_content = BytesIO(response.content)
            return send_file(file_content, mimetype=mime_type, as_attachment=True, download_name=filename)
        
    except requests.RequestException as e:
        print(f"Error fetching file: {e}")
        return render_template('index.html', status='Unable to Download', user=session['username'], data=retrive(session['username']))

@app.route('/fuck_off', methods=['GET', 'POST'])
def fuck_off():
    file_name = request.form["file_name"]
    
    result = delete_file(session['username'],file_name)
    
    if result:
             return render_template('index.html', status='Removed', user=session['username'], data=retrive(session['username']))
    
    return render_template('index.html', status='Unable to Remove', user=session['username'], data=retrive(session['username']))

 
if __name__ == '__main__':
    app.run(debug=True)
