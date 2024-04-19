import flask
from flask import Flask, render_template, request, redirect, url_for, abort, session
from sqlalchemy import create_engine, text
from random import randint

app = Flask(__name__)
conn_str = 'mysql://root:cset155localhost/ecommerce'
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'hello'


@app.route('/')
def homepage():
    return render_template('base.html')


@app.route('/register', methods=['GET','POST'])
def create_account():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email_address = request.form.get('email_address')
        
        conn.execute(text(
            'INSERT INTO accounts (name, userName, email, phone_number, password) VALUES (name, :username, :email_address, :password)'),
            {'name': name, 'username': username, 'email': email, 'password': password})
        conn.commit()
        return render_template("register.html")
    else:
        return render_template("register.html")





if __name__ == '__main__':
    app.run(debug=True)