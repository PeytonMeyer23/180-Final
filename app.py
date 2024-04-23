from flask import Flask, render_template, request, redirect, session
from sqlalchemy import create_engine, text
from flask_bcrypt import Bcrypt #pip install Flask-Bcrypt

app = Flask(__name__)

conn_str = "mysql://root:9866@localhost/ecommerce"
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'hello'
bcrypt = Bcrypt(app)


@app.route('/')
def homepage():
    return render_template('base.html')

# account functionality
@app.route('/register', methods=['GET','POST'])
def create_account():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        accountType = request.form.get('accountType')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        cursor = conn.execute(f"SELECT * FROM User WHERE email = '{email}'")
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "Email already exists."
            return render_template('register.html', error_message=error_message)
        
        conn.execute(text(
            'INSERT INTO user (name, username, password, email, accountType) VALUES (:name, :username, :password, :email, :accountType)'),
            {'name': name, 'username': username, 'email': email, 'password': hashed_password, 'accountType': accountType})
        conn.commit()
        return render_template("register.html")
    else:
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['input']
        password = request.form['password']

        query = (f"SELECT accountType FROM user WHERE username = {username_or_email} OR email = {username_or_email} AND password = {password}")
        result = conn.execute(query, (username_or_email, username_or_email, password)).fetchone()

        if result:
            role = result[0]  # role from the result
            session['username_or_email'] = username_or_email
            session['role'] = role
            if role == 'vendor':
                return render_template(vendor.html)
        elif role == 'user':
            return render_template(user.html)
        elif role == 'admin':
            return render_template(admin.html)
        else:
            error_message = "Invalid username/email or password"
            return render_template('login.html', error_message=error_message)
    # return render_template('login.html')


@app.route('/signout', methods=['GET', 'POST'])
def signout():
    if request.method == 'POST':
        session.clear()
        return redirect('login')
    

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if request.method == 'POST':
        productIDD = request.form.get('productID')
        size = request.form.get('size')
        color = request.form.get('color')
        quantity = int(request.form.get('quantity', 1))
        return render_template('cart.html')


# vendor
@app.route('/products')
def get_products():
    products = conn.execute(text("SELECT * FROM product")).fetchall()
    return render_template("products.html", products=products)



# filter
# @app.route('/filter', methods=['POST'])
# def search_account():
# if request.method == 'POST':
#     x = request.form['type']
#     account_info = conn.execute(text(f"SELECT * FROM users WHERE type = :type"), {'type': x}).fetchall()
#     return render_template('filter.html', info_type=account_info)


if __name__ == '__main__':
    app.run(debug=True)