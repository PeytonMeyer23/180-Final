import flask
from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, text

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
        email = request.form.get('email')
        accountType = request.form.get('accountType')
        
        conn.execute(text(
            'INSERT INTO accounts (name, username, password, email) VALUES (name, :username, :password, :email)'),
            {'name': name, 'username': username, 'email': email, 'password': password})
        conn.commit()
        return render_template("register.html")
    else:
        return render_template("register.html")


# @app.route('/(PAGETITLE)')
# def add_product():






if __name__ == '__main__':
    app.run(debug=True)