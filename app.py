from flask import Flask, render_template, request, redirect, session, url_for, jsonify       
from sqlalchemy import create_engine, text
from werkzeug.security import check_password_hash, generate_password_hash
import uuid
import datetime

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/ecommerce"

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
                return redirect(url_for("dashboard"))
            elif role == 'user':
                return redirect(url_for("products"))
            elif role == 'admin':
                return redirect(url_for("dashboard"))
        else:
            error_message = "Invalid username/email or password"
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')


@app.route('/signout', methods=['GET', 'POST'])
def signout():
    if request.method == 'POST':
        session.clear()
        return redirect('signout')
    

@app.route('/products', methods=['GET', 'POST'])
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

        sort = request.form.get('sort', 'date')

        if sort == 'date':
            reviews = conn.execute(
                text("SELECT * FROM review ORDER BY date DESC")
            ).fetchall()
        elif sort == 'rating':
            reviews = conn.execute(
                text("SELECT * FROM review ORDER BY rating DESC")
            ).fetchall()

    return render_template('products.html', products=products, reviews=reviews)


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
    image_urls = request.form.getlist('Image URL')

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

    # Insert all image URLs at once
    conn.execute(
        text("INSERT INTO productimages (productID, imageURL) VALUES (:productID, :imageURL)"),
        [{'productID': product_id, 'imageURL': url} for url in image_urls]
    )

    conn.commit()
    return render_template('products.html')



@app.route('/order', methods=['GET'])
def MakeOrder(user, cart_items):

    order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = "placed"  
    placed_by_username = user
    conn.execute(
        text("select * from cart where ")
    )
    cartWithProducts = ""


    conn.execute(
        text("INSERT INTO orders (date, status, placedByUserName) VALUES (:date, :status, :placedByUserName)"),
        {'date': order_date, 'status': status, 'placedByUserName': placed_by_username}
    )

# chat
@app.route('/chat', methods=['POST', 'GET'])
def chat():
    error_message = None
    success_message = None
    if request.method == 'POST':
        if 'user' in session:
            current_user = session['user']
            receiverUserName = request.form['receiverUserName']
            text_message = request.form['text']
            imageURL = request.form['imageURL']

            # get vendor
            if receiverUserName != current_user:
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
                success_message = 'Message sent!'
            else:
                error_message = 'You cannot send a message to yourself'

    return render_template('chat.html', error_message=error_message, success_message=success_message)    


@app.route('/show_chat', methods=['POST', 'GET'])
def show_chat():
    if request.method == 'GET':
        current_user = session['user']
        chats = conn.execute(text('SELECT * FROM message WHERE (receiverUserName = :current_user OR writerUserName = :current_user)'), {'current_user': current_user})
        return render_template('show_chat.html', show_chats=chats)
    return render_template('show_chat.html', show_chats=[])


@app.route('/reply', methods=['POST', 'GET'])
def send_message():
    error_message = None
    success_message = None
    if request.method == 'POST':
        if 'user' in session:
            current_user = session['user']
            send_to = request.form['reply']
            receiverUserName = request.form['receiverUserName']
            if current_user != receiverUserName:
                conn.execute(
                    text('INSERT INTO message (writerUserName, receiverUserName, text) VALUES (:current_user, :receiverUserName, :send_to)'),
                    {'current_user': current_user, 'receiverUserName': receiverUserName, 'send_to': send_to}
                )
                conn.commit()
                success_message = 'Message sent!'
        else:
            error_message = 'You cannot reply to yourself.'
        
    return render_template("show_chat.html", success_message=success_message, error_message=error_message)
        

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


@app.route('/update_product', methods=['GET', 'POST'])
def update_product():
    if request.method == 'POST':
        if 'user' in session:
            current_user = session['user']
            x = request.form['ProductID']
            name = request.form['ProductName']
            description = request.form['Description']
            warranty = request.form['WarrantyPeriod']
            number = request.form['NumberOfItems']
            price = request.form['Price']
            imageURL = request.form['ImageURL']
            product = conn.execute(text(f'SELECT * FROM product WHERE productID = {x}'))
            conn.execute(
                text("UPDATE product SET title = :name, description = :description, warrantyPeriod = :warranty, numberOfItems = :number, price = :price, addedByUserName = :current_user WHERE productID = :x"),
                {'name': name, 'description': description, 'warranty': warranty, 'number': number, 'price': price, 'current_user': current_user, 'x': x}
            )
            conn.execute(
                text("UPDATE productimages SET imageURL = :imageURL WHERE productID = :x"),
                {'imageURL': imageURL, 'x': x}
            )
            conn.commit()
            return render_template('update_product.html')
    else:
        return render_template('update_product.html')

#delete
@app.route('/delete_product', methods=["GET", "POST"])
def delete_product():
    if request.method == "POST":
        productID = request.form['productID']
        conn.execute(text("DELETE FROM productimages WHERE productID = :productID"), {'productID': productID})
        conn.execute(text("DELETE FROM product WHERE productID = :productID"), {'productID': productID})
        conn.commit()

        return redirect(url_for("delete_product"))
    else:
        return render_template("delete_product.html")
    

@app.route('/home')
def home():
    return render_template("home.html")

# @app.route('/info', methods=["GET"])
# def account_info():
#     if request.method == "GET":
#         user = session['user']
#         result = conn.execute(text("SELECT * FROM user WHERE userName = :user"), {'user': user})
#         accounts = [dict(row) for row in result]
#         return render_template("account_info.html", result=accounts)
#     return render_template("account_info.html", accounts=[])



@app.route('/info', methods=['POST', 'GET'])
def account_info():
    if 'user' not in session:
        # Handle this case appropriately, redirect to login maybe
        return "User not logged in."

    if request.method == 'GET':
        current_user = session['user']
        result = conn.execute(text("SELECT * FROM user WHERE userName = :user"), {'user': current_user}).fetchall()
        if not result:
            return "No user found"
        return render_template('account_info.html', user=result[0])
    
    return render_template('account_info.html', user={})  # Empty user in case of POST request


@app.route('/review', methods=['POST', 'GET'])
def review():
    if 'user' in session:
        if request.method == 'POST':
            reviewUserName = session['user']
            rating = request.form['rating']
            description = request.form['desc']
            img = request.form['img']
            date = datetime.datetime.now().strftime("%Y-%m-%d")
            conn.execute(
                text("insert into review (rating, description, img, date, reviewUserName) VALUES "
                     "(:rating, :description, :img, :date, :reviewUserName)"),
                {
                    'rating': rating,
                    'description': description,
                    'img': img,
                    'date': date,
                    'reviewUserName': reviewUserName
                }
            )
            conn.commit()

        return render_template('review.html')
    else:
        return redirect(url_for('login'))

    


if __name__ == '__main__':
    app.run(debug=True)