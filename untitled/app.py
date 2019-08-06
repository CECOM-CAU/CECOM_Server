from flask import Flask, url_for, render_template, request, redirect, session
import sqlite3
import os
import socket
import datetime

from werkzeug.utils import secure_filename
DB_UPLOAD_FOLDER = "./database"
UPLOAD_FOLDER = "./upload"
app = Flask(__name__)
app.secret_key = 'We are Fried Chicken Dinner!!!!'
fileLogDB = 'fileUploadLog.db'

@app.route('/')
def hello_world():
    session['user'] = ""
    return 'Hello World!'

@app.route('/upload', methods=['GET', 'POST'])
def uploadPage():
    if request.method == 'POST':
        conn = sqlite3.connect(os.path.join(DB_UPLOAD_FOLDER, fileLogDB))
        curs = conn.cursor()
        curs.execute("SELECT * FROM fileLogDB")
        item = request.files['itemPhoto']
        path = ""
        if 'itemSearch' in request.form:
            path = request.form['itemPath']
        if not os.path.isdir(DB_UPLOAD_FOLDER):
            os.mkdir(DB_UPLOAD_FOLDER)
        fileName = item.filename.replace("../", "")
        """
         subFileName = ""
        if(fileName[0] == '.'):
            subFileName = '.'
        """

        print(fileName)
        saveFilePath = os.path.join(UPLOAD_FOLDER,path)
        item.save(os.path.join(saveFilePath,fileName))
        curs.execute("insert into fileLogDB values ('" + session['user'] + "', '" + str(datetime.datetime.now())[:19] + "', '" + os.path.join(saveFilePath,fileName) + "')")
        conn.commit()
        conn.close()
        return 'success'
    elif request.method == 'GET':
        #if session['user'] == "":
         #   return "로그인이 필요합니다."
        return render_template('ItemUpload.html')


def DBinit():
    if not os.path.isdir(DB_UPLOAD_FOLDER):
        os.mkdir(DB_UPLOAD_FOLDER)
    if not os.path.isfile(os.path.join(DB_UPLOAD_FOLDER, fileLogDB)):
        conn = sqlite3.connect(os.path.join(DB_UPLOAD_FOLDER, fileLogDB))
        curs = conn.cursor()
        curs.execute("CREATE TABLE  if not exists fileLogDB(username, time, file)")
        conn.commit()
        conn.close()


if __name__ == '__main__':
    IP = str(socket.gethostbyname(socket.gethostname()))
    DBinit()
    app.run(host=IP, port=5010, debug=True)