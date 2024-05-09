from flask import Flask, render_template, request, redirect, session, url_for,jsonify       
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import uuid
app = Flask(__name__)

# conn_str = "mysql://root:CSET@localhost/ecomerce"

conn_str = "mysql://root:9866@localhost/ecommerce"


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

if __name__ == '__main__':
    app.run(debug=True)
# account functionality
@app.route('/register.html', methods=['GET','POST'])
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


@app.route('/login.html', methods=['GET', 'POST'])
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
                return redirect(url_for("chat"))
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
    if request.method == 'POST':
        keyword = request.form['q']
        query = text("SELECT p.productID, p.title, p.description, p.warrantyPeriod, p.numberOfItems, p.price, pi.imageURL "
                     "FROM product p LEFT JOIN productimages pi ON p.productID = pi.productID "
                     "WHERE p.title LIKE :keyword OR p.description LIKE :keyword")
        products = conn.execute(query, {'keyword': '%' + keyword + '%'}).fetchall()
    else:
        products = conn.execute(
            text("SELECT p.productID, p.title, p.description, p.warrantyPeriod, p.numberOfItems, p.price, pi.imageURL "
                 "FROM product p LEFT JOIN productimages pi ON p.productID = pi.productID")
        ).fetchall()

    return render_template('products.html', products=products)



@app.route('/update-cart', methods=['POST'])
def update_cart():
    cart_data = request.get_json()
    cartID = cart_data['cartID']
   


@app.route('/products_test')
def test_products2():
    products = conn.execute(
        text("SELECT p.productID, p.title, p.description, p.warrantyPeriod, p.numberOfItems, p.price, pi.imageURL "
             "FROM product p LEFT JOIN productimages pi ON p.productID = pi.productID")
    ).fetchall()
    
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

def MakeOrder(user, cart_items):

    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "placed"  
    placed_by_username = user  


    conn.execute(
        text("INSERT INTO orders (date, status, placedByUserName) VALUES (:date, :status, :placedByUserName)"),
        {'date': order_date, 'status': status, 'placedByUserName': placed_by_username}
    )
    

    order_id = conn.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]




# @app.route('/cart', methods=['POST'])
# def AddCart():
#     if request.method == 'POST':
#         productID = request.form.get('productID')
#         size = request.form.get('size')
#         color = request.form.get('color')
#         quantity = int(request.form.get('quantity', 1))
#         return render_template('cart.html')



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
    

@app.route('/show_chat', methods=['POST', 'GET'])
def show_chat():
    if request.method == 'GET':
        current_user = session['user']
        chats = conn.execute(text('SELECT * FROM message WHERE (receiverUserName = :current_user)'), {'current_user': current_user})
        return render_template('show_chat.html', show_chats=chats)
    return render_template('show_chat.html', show_chats=[])


@app.route('/reply', methods=['POST', 'GET'])
def send_message():
    if request.method == 'POST':
        if 'user' in session:
            current_user = session['user']
            send_to = request.form['reply']
            receiverUserName = request.form['receiverUserName']
            conn.execute(
    text('INSERT INTO message (writerUserName, receiverUserName, text) VALUES (:current_user, :receiverUserName, :send_to)'),
    {'current_user': current_user, 'receiverUserName': receiverUserName, 'send_to': send_to}
)
            conn.commit()
            return render_template('show_chat.html')
    else:
        return render_template('show_chat.html')




@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('productID')

    # Generate unique cart ID for the user
    cart_id = str(uuid.uuid4())

    # Insert into cart table
    print("Inserting into cart table:", cart_id)
    conn = engine.connect()
    conn.execute(
        text("INSERT INTO cart (cartID) VALUES (:cartID)"),
        {'cartID': cart_id}
    )

    # Insert into carthasproduct table
    print("Inserting into carthasproduct table:", cart_id, product_id)
    conn.execute(
        text("INSERT INTO carthasproduct (cartID, productID, size, color) VALUES "
             "(:cartID, :productID, :size, :color)"),
        {
            'cartID': cart_id,
            'productID': product_id,
            'size': 1,  # Hardcoded for now
            'color': 1,  # Hardcoded for now
        }
    )

    conn.close()

    return 'Product added to cart successfully'



if __name__ == '__main__':
    app.run(debug=True)