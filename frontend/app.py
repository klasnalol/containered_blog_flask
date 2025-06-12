from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='Blog Feed')

@app.route('/login')
def login():
    return render_template('login.html', title='Login')

@app.route('/register')
def register():
    return render_template('register.html', title='Register')

@app.route('/upload')
def upload():
    return render_template('upload.html', title='Create Post')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=443, ssl_context=('certs/server.crt', 'certs/server.key'))
