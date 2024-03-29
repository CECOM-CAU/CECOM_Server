from datetime import datetime
from flask import Flask, url_for, render_template, request, redirect, session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
import socket

from werkzeug.utils import secure_filename
DB_UPLOAD_FOLDER = "./database"
UPLOAD_FOLDER = "./upload"
app = Flask(__name__)
app.secret_key = 'We are Fried Chicken Dinner!!!!'
fileLogDB = 'fileUploadLog.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login = LoginManager(app)

class User(db.Model):
    __table_name__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    profile_image = db.Column(db.String(100), default='default.png')

    posts = db.relationship('Post', backref='author', lazy=True)

    def __init__(self, username, email, password, **kwargs):
        self.username = username
        self.email = email

        self.set_password(password)

    def __repr__(self):
        return f"<User('{self.id}', '{self.username}', '{self.email})>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Post(db.Model):
    __table_name__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"<Post('{self.id}', '{self.title}')>"


class File():
    def __init__(self, name, path, type, ctime):
        self.name = name
        self.path = path
        self.type = type
        self.ctime = ctime


@app.route('/')
def init():
    logout()
    return render_template('home.html')


@app.route('/home')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        curr_user = User.query.filter_by(username=session['name']).first()
        return render_template('home.html', curr_user=curr_user)


@app.route('/index')
def index():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')


@app.route('/introduction')
def introduction():
    return render_template('introduction.html')


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        session['name'] = request.form['username']
        passw = request.form['password']

        user = User.query.filter_by(username=name).first()

        if user is not None and user.check_password(passw):
            session['logged_in'] = True
            curr_user = user
            return render_template('home.html', curr_user=curr_user)
        else:
            return render_template('login.html')


@app.route('/logout')
def logout():
    session['logged_in'] = False
    session.pop('username',None)
    return redirect(url_for('login'))


@app.route('/regi', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], email=request.form['email'], password=request.form['password'] )
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html')
    return render_template('register.html')


@app.route('/description', methods=['GET','POST'])
def description():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        users = User.query.all()
        curr_user = User.query.filter_by(username=session['name']).first()
        if request.method == 'POST':
            delete()
        return render_template('description.html', users=users, curr_user=curr_user, title='Description')


def delete():
    delete_user = User.query.filter_by(username=request.form['delete_username']).first()
    if delete_user is not None and delete_user.check_password(request.form['password']):
        db.session.delete(delete_user)
        db.session.commit()
        if request.form['delete_username'] == session['name']:
            logout()
            return redirect(url_for('description'))
        return redirect(url_for('description'))



@app.route('/archive/', defaults={'path':''}, methods=['GET','POST'])
@app.route('/archive/<path:path>')
def archive(path):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.path == url_for('archive'):
            years = getFolders('upload')
            index = len(years)-1
            now = years[index]
            return render_template('carousel.html', now=now, years=years, title='About')
        else:
            years = getFolders('upload')
            index = len(years)-1
            now = years[index]
            mypath = os.path.join('upload', path)
            files = getFiles(mypath)
            return render_template('archive.html', path=path , now=now, years=years, files=files, title='About')


def getFiles(path):
    fileList = os.listdir(path)
    files = []
    for file in fileList:
        s = file.split('.')
        _path = os.path.join(path, file)
        #_path = path + '/' + file
        if len(s) != 1:
            fType = s[-1].upper()
        else:
            fType = 'FOLDER'
        f = File(name=file, path=_path, type=fType, ctime=os.stat(path=_path).st_ctime)
        files.append(f)
    return files


def getFolders(path):
    fileList = os.listdir(path)
    folders = []
    for file in fileList:
        s = file.split('.')
        _path = os.path.join(path, file)
        if len(s) == 1:
            fType = 'FOLDER'
            f = File(name=file, path=_path, type=fType, ctime=os.stat(path=_path).st_ctime)
            folders.append(f)
    return folders




@app.route('/upload/', defaults={'tempPath':''}, methods=['GET', 'POST'])
@app.route('/upload/<path:tempPath>', methods=['GET', 'POST'])
def uploadPage(tempPath):
    #print("asdf :" + str(tempPath))
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        folders=getFolders('upload' + '/' + tempPath)

        if request.method == 'POST':
            print('post')
            #conn = sqlite3.connect(os.path.join(DB_UPLOAD_FOLDER, fileLogDB))
            #curs = conn.cursor()
            #curs.execute("SELECT * FROM fileLogDB")
            items = request.files.getlist('itemPhoto')

            if len(items) == 0:
                return render_template('uploadPage.html', path=tempPath, folders=folders)

            if not os.path.isdir(DB_UPLOAD_FOLDER):
                os.mkdir(DB_UPLOAD_FOLDER)
            """
             subFileName = ""
            if(fileName[0] == '.'):
                subFileName = '.'
            """

            #print(fileName)
            saveFilePath = os.path.join(UPLOAD_FOLDER,tempPath)
            newDir = request.form['newDir']
            if newDir != '':
                tempPath = tempPath + '/' + newDir
                saveFilePath = os.path.join(UPLOAD_FOLDER, tempPath)
                os.mkdir(saveFilePath)

            for item in items:
                item.save(os.path.join(saveFilePath,item.filename.replace("../", "")))
            #curs.execute("insert into fileLogDB values ('" + session['name'] + "', '" + str(datetime.now())[:19] + "', '" + os.path.join(saveFilePath,fileName) + "')")
            #conn.commit()
            #conn.close()
            return redirect(url_for('archive', path=tempPath))
        elif request.method == 'GET':
            print(tempPath)
            if session['logged_in'] == False:
                return url_for('login')
            #if tempPath != '':
            #    tempPath = '/' + tempPath
            return render_template('uploadPage.html', path=tempPath, folders=folders)

def DBinit():
    if not os.path.isdir(DB_UPLOAD_FOLDER):
        os.mkdir(DB_UPLOAD_FOLDER)
    if not os.path.isfile(os.path.join(DB_UPLOAD_FOLDER, fileLogDB)):
        conn = sqlite3.connect(os.path.join(DB_UPLOAD_FOLDER, fileLogDB))
        curs = conn.cursor()
        curs.execute("CREATE TABLE  if not exists fileLogDB(username, time, file)")
        conn.commit()
        conn.close()

def Download():
    pass

if __name__ == '__main__':
    IP = str(socket.gethostbyname(socket.gethostname()))
    DBinit()
    app.run(host=IP, port=5010, debug=True)