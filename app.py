from flask import Flask, render_template, request, redirect, session, url_for
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

conn_str = "mysql://root:cset155@localhost/ecommerce"


engine = create_engine(conn_str, echo = True)
conn = engine.connect()
app.secret_key = 'hello'

@app.route('/', methods=['GET', 'POST'])
def test_products():
    if request.method == 'POST':
        cart_data = request.get_json()
        cart_id = cart_data['cartID']
        product_id = cart_data['productID']
        size = cart_data['size']
        color = cart_data['color']
        
        # Insert the cart item into the database
        conn.execute(
            text("INSERT INTO carthasproduct (cartID, productID, size, color) VALUES (:cart_id, :product_id, :size, :color)"),
            cart_id=cart_id,
            product_id=product_id,
            size=size,
            color=color
        )
        
        return {'message': 'Cart item added successfully'}
    
    else:
        products = conn.execute(
            text("SELECT p.productID, p.title, p.description, p.warrantyPeriod, p.numberOfItems, p.price, pi.imageURL "
                 "FROM product p LEFT JOIN productimages pi ON p.productID = pi.productID")
        ).fetchall()
        
        return render_template('index.html', products=products)



# account functionality
@app.route('/register', methods=['GET','POST'])
def create_account():
    if request.method == "POST":
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        accountType = request.form.get('accountType')
        hashed_password = generate_password_hash(password)
        
        cursor = conn.execute(text("SELECT * FROM user WHERE email = :email"), {'email': email})
        existing_user = cursor.fetchone()
        if existing_user:
            error_message = "Email already exists."
            return render_template('register.html', error_message=error_message)
        
        conn.execute(text(
            'INSERT INTO user (name, username, password, email, accountType) VALUES (:name, :username, :password, :email, :accountType)'),

            {'name': name, 'username': username, 'email': email, 'password': hashed_password, 'accountType': accountType})

        conn.commit()
        return redirect(url_for("login"))
    else:
        return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['input']
        password = request.form['password']

        query = text("SELECT userName, accountType, password FROM user WHERE (email = :input OR userName = :input)")
        result = conn.execute(query, {'input': username_or_email}).fetchone()

        if result and check_password_hash(result[2], password):
            user = result[0]
            role = result[1]
            session['user'] = user
            session['username_or_email'] = username_or_email
            session['role'] = role
            if role == 'vendor':
                return redirect(url_for("products"))
            elif role == 'user':
                return redirect(url_for("chat"))
            elif role == 'admin':
                return redirect(url_for("products"))
        else:
            error_message = "Invalid username/email or password"
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')


@app.route('/signout', methods=['GET', 'POST'])
def signout():
    if request.method == 'POST':
        session.clear()
        return redirect('login')
    

@app.route('/products')
def products():
    products = conn.execute(
        text("SELECT p.productID, p.title, p.description, p.warrantyPeriod, p.numberOfItems, p.price, pi.imageURL "
             "FROM product p LEFT JOIN productimages pi ON p.productID = pi.productID")
    ).fetchall()
    
    return render_template('products.html', products=products)


# @app.route('/products_test')
# def test_products():
#     products = conn.execute(
#         text("SELECT p.productID, p.title, p.description, p.warrantyPeriod, p.numberOfItems, p.price, pi.imageURL "
#              "FROM product p LEFT JOIN productimages pi ON p.productID = pi.productID")
#     ).fetchall()
    
#     return render_template('product_page_test.html', products=products)

@app.route('/addproducts', methods=['GET'])
def add_products():
    return render_template('addproduct.html')


@app.route('/addproducts', methods=['POST'])
def create_product():
    product_id = request.form.get('Product ID')
    title = request.form.get('Product Name')
    description = request.form.get('Description')
    warranty_period = request.form.get('Warranty Period')
    number_of_items = request.form.get('Number Of Items')
    price = request.form.get('Price')
    image_urls = request.form.getlist('Image URL')  # Get list of image URLs from the form

    # Insert into product table
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
    
    # Insert into productimages table for each image URL
    for url in image_urls:
        conn.execute(
            text("INSERT INTO productimages (productID, imageURL) VALUES (:productID, :imageURL)"),
            {
                'productID': product_id,
                'imageURL': url
            }
        )

    conn.commit()
    return render_template('products.html')


# # vendor
# @app.route('/products')
# def get_products():
#     products = conn.execute(text("SELECT * FROM product")).fetchall()
#     return render_template("products.html", products=products)


# filter
# @app.route('/filter', methods=['POST'])
# def search_account():
# if request.method == 'POST':
#     x = request.form['type']
#     account_info = conn.execute(text(f"SELECT * FROM users WHERE type = :type"), {'type': x}).fetchall()
#     return render_template('filter.html', info_type=account_info)

# chat
@app.route('/chat', methods=['POST', 'GET'])
def chat():
    if request.method == 'POST':
        if 'user' in session:
            current_user = session['user']
            receiverUserName = request.form['receiverUserName']
            text_message = request.form['text']
            imageURL = request.form['imageURL']

            # get vendor
            query_text = text("SELECT userName FROM user WHERE userName = :receiverUserName AND accountType = 'vendor'")
            result = conn.execute(query_text, {'receiverUserName': receiverUserName}).fetchone()
            if result:
                vendor_username = result[0]

            # insert message into SQL
            conn.execute(
                text("INSERT INTO message (text, imageURL, writerUserName, receiverUserName) VALUES "
                     "(:text, :imageURL, :writerUserName, :receiverUserName)"),
                {
                    'writerUserName': current_user,
                    'receiverUserName': receiverUserName,
                    'text': text_message,
                    'imageURL': imageURL
                }
            )
            conn.commit()
            return render_template('chat.html')
    else:
        return render_template('chat.html')


if __name__ == '__main__':
    app.run(debug=True)