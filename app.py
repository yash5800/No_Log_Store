from flask import Flask, render_template, request, session, send_file
from sql_operations import *
from io import BytesIO
import mimetypes
import os
import secrets

import dropbox

# Initialize Dropbox client with access token
dbx = dropbox.Dropbox(os.getenv('BOX'))

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

def get_remaining_storage():
    try:
        usage = dbx.users_get_space_usage()
        
        # Total allocated storage in bytes
        allocated = usage.allocation.get_individual().allocated
        # Used storage in bytes
        used = usage.used
        # Remaining storage in bytes
        remaining = allocated - used
        
        # Convert bytes to MB for readability
        allocated_mb = allocated / (1024 * 1024)
        used_mb = used / (1024 * 1024)
        remaining_mb = remaining / (1024 * 1024)
        
        print(f"\nTotal Storage: {allocated_mb:.2f} MB")
        print(f"Used Storage: {used_mb:.2f} MB")
        print(f"Remaining Storage: {remaining_mb:.2f} MB\n")
        
        space =  {
                "total_mb": round(allocated_mb,2),
                "used_mb": round(used_mb,2),
                "remaining_mb": round(remaining_mb,2)
               }
        
        session['space'] = space
        

        
    except dropbox.exceptions.ApiError as e:
        print(f"Error fetching storage info: {e}")
        return None


@app.route('/')
def main():
    return render_template('key.html')

@app.route('/check_shit', methods=['POST', 'GET'])
def check_shit():
    
    get_remaining_storage()
    
    session['username'] = request.form['key']
    print(session['username'])
    
    data = retrive(session['username'])
    if data == 'new':
        return render_template('index.html', user=session['username'])
    
    return render_template('index.html', user=session['username'], data=data,space=session['space'])

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

        # Check the file size
        file_content = file.read()
        file_name = file.filename

        try:
            dbx.files_upload(file_content, f'/uploads/{file_name}', mute=True)
            insert(session['username'], file_name)
            
            get_remaining_storage()
            return render_template('index.html', status='uploaded', user=session['username'], data=retrive(session['username']),space=session['space'])
        
        except dropbox.exceptions.ApiError as e:
            print(f"Dropbox API error: {e}")
            return render_template('index.html', status='Upload failed', user=session['username'], data=retrive(session['username']),space=session['space'])


@app.route('/download', methods=['GET', 'POST'])
def download_file():
    file_name = request.form["file_name"]
    print("Downloading file:", file_name)

    try:
        metadata, response = dbx.files_download(f'/uploads/{file_name}')
        mime_type, _ = mimetypes.guess_type(file_name)
        file_content = BytesIO(response.content)

        return send_file(file_content, mimetype=mime_type, as_attachment=True, download_name=file_name)
    
    except dropbox.exceptions.ApiError as e:
        print(f"Error fetching file: {e}")
        return render_template('index.html', status='Unable to Download', user=session['username'], data=retrive(session['username']))
    
@app.route('/view', methods=['GET', 'POST'])
def view():
    file_name = request.form["file_name"]

    try:
        metadata, response = dbx.files_download(f'/uploads/{file_name}')
        temp_pdf_path = 'temp_pdf.pdf'
        with open(temp_pdf_path, 'wb') as f:
            f.write(response.content)
        return render_template('view_pdf.html', pdf_path=temp_pdf_path)
    
    except dropbox.exceptions.ApiError as e:
        print(f"Error fetching file: {e}")
        return "Failed to retrieve the PDF."

@app.route('/display/<path:pdf_path>')
def display_pdf(pdf_path):
    return send_file(pdf_path, as_attachment=False)

@app.route('/fuck_off', methods=['GET', 'POST'])
def fuck_off():
    file_name = request.form["file_name"]
    print("Deleting file:", file_name)

    try:
        dbx.files_delete_v2(f'/uploads/{file_name}')
        delete_file(session['username'], file_name)
        
        get_remaining_storage()
        return render_template('index.html', status='Removed', user=session['username'], data=retrive(session['username']),space=session['space'])
    
    except dropbox.exceptions.ApiError as e:
        print(f"Error deleting file: {e}")
        return render_template('index.html', status='Unable to Remove', user=session['username'], data=retrive(session['username']),space=session['space'])


if __name__ == '__main__':
        app.run()
