from flask import Flask,render_template,url_for,request,g,redirect,session
from git_repo import upload_to_github
from sql_operations import *

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
        success = upload_to_github(file_content, file_name)
        

        
        print("File upload success:", success)
       
        
        if success:
            insert(session['username'], file_name)
            return render_template('index.html', status='uploaded', user=session['username'], data=retrive(session['username']))
        else:
            return render_template('index.html', status='Not uploaded/File Name Already exists', user=session['username'], data=retrive(session['username']))


 
if __name__ == '__main__':
    app.run(debug=True)
