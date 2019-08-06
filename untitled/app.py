from flask import Flask
from flask import Flask, url_for, render_template, request, redirect, session
from werkzeug.utils import secure_filename


app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/upload', methods=['GET', 'POST'])
def uploadPage():
    if request.method == 'POST':
        item = request.files['itemPhoto']
        fileName = item.filename
        subFileName = ""
        if(fileName[0] == '.'):
            subFileName = '.'
        print(fileName)
        item.save("./upload/"+subFileName+fileName)
        return 'success'
    elif request.method == 'GET':
        return render_template('ItemUpload.html')


if __name__ == '__main__':
    app.run()
