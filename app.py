from flask import Flask, render_template, request, redirect, session
from sqlalchemy import create_engine, text

app = Flask(__name__)

conn_str = "mysql://root:9866@localhost/ecommerce"
engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'hello'


@app.route('/')
def homepage():
    return render_template('base.html')

# accounts
@app.route('/register', methods=['GET','POST'])
def create_account():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        accountType = request.form.get('accountType')
        
        conn.execute(text(
            'INSERT INTO user (name, username, password, email, accountType) VALUES (:name, :username, :password, :email, :accountType)'),
            {'name': name, 'username': username, 'email': email, 'password': password, 'accountType': accountType})
        conn.commit()
        return render_template("register.html")
    else:
        return render_template("register.html")

@app.route('/products')
def get_products():
    products = conn.execute(text("SELECT * FROM product")).fetchall()
    return render_template("products.html", products=products)
# @app.route('/(PAGETITLE)')
# def add_product():


@app.route('/addproducts', methods=['GET'])
def add_products  ():
    return render_template('addproduct.html')



@app.route('/addproducts', methods=['POST'])
def create_product():
    product_id = request.form.get('Product ID')
    title = request.form.get('Product Name')
    description = request.form.get('Description')
    warranty_period = request.form.get('Warranty Period')
    number_of_items = request.form.get('Number Of Items')
    price = request.form.get('Price')

    conn.execute(
        text("INSERT INTO product (productID, title, description, warrantyPeriod, numberOfItems, price) VALUES "
             "(:productID, :title, :description, :warrantyPeriod, :numberOfItems, :price)"),
        {
            'productID': product_id,
            'title': title,
            'description': description,
            'warrantyPeriod': warranty_period,
            'numberOfItems': number_of_items,
            'price': price
        }
    )
    conn.commit()
    return render_template('products.html')


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
            return redirect ('register.html') # Replace register.html. Redirect to dashboard or home page.
        else:
            error_message = "Invalid username/email or password"
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')


@app.route('/signout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()



# filter
# @app.route('/filter', methods=['GET'])
# def searches():
#     return flask.render_template('filter.html', info_type=[])


# @app.route('/filter', methods=['POST'])
# def search_account():
#     x = request.form['type']
#     account_info = conn.execute(text(f"SELECT * FROM users WHERE type = :type"), {'type': x}).fetchall()
#     return render_template('filter.html', info_type=account_info)

        # user = request.form.get('user')
        # session["user"] = user
        # print(session['user'])
        # password = request.form['password']
        # if user == 'admin' and password == 'CaptainCommerce':
        #     return redirect('accounts_page')
        # else:
        #     return redirect('login.html')

if __name__ == '__main__':
    app.run(debug=True)