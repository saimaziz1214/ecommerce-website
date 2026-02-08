from flask import Flask, render_template, request,session
import mysql.connector
from flask import jsonify
from flask import Flask,render_template,redirect,url_for,session,flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
import bcrypt

import email_validator

from dashboard import init_dashboard



app =Flask(__name__)

app.secret_key = 'your_super_secret_key'
dash_app = init_dashboard(app) 

def get_db_connection():
    import mysql.connector
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password='',
        database="afashion"
    )

@app.route('/')  
def home():
    return render_template('home.html')

@app.route('/about')  
def about():
    return render_template('about.html')

@app.route('/dashboard-page')
def dashboard_page():
    return render_template('dashboard.html')


@app.route('/account')  
def account():
    return render_template('account.html')



class RegistrationForm(FlaskForm):
    name = StringField('Name',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
  
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Register')


    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO users(name,email,password) VALUES(%s,%s,%s)",
            (name, email, hashed_password)
        )
        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# ------------------------------
# LOGIN ROUTE
# ------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        db.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['user_id'] = user['ID']  # user ID from DB
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

@app.route('/shop')
def shop():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get filters from query params
    selected_category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    # Fetch categories
    cursor.execute("SELECT category_name FROM categories")
    categories = [row['category_name'] for row in cursor.fetchall()]

    # Base query
    query = """
        SELECT p.*
        FROM products p
        JOIN subcategories s ON p.subcategory_id = s.subcategory_id
        JOIN categories c ON s.category_id = c.category_id
        WHERE 1=1
    """
    params = []

    # Apply category filter
    if selected_category:
        query += " AND c.category_name = %s"
        params.append(selected_category)

    # Apply price filters
    if min_price is not None:
        query += " AND p.price >= %s"
        params.append(min_price)

    if max_price is not None:
        query += " AND p.price <= %s"
        params.append(max_price)

    # Optional limit
    query += " LIMIT 200"

    cursor.execute(query, tuple(params))
    products = cursor.fetchall()

    return render_template(
        'shop.html',
        products=products,
        categories=categories,
        selected_category=selected_category,
        min_price=min_price,
        max_price=max_price
    )




@app.route('/cart', methods=['POST'])
def cart():
    if 'user_id' not in session:
        return jsonify({'message': 'Please login first'}), 401

    user_id = session['user_id']
    product_id = request.form.get('product_id')

   
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    # Check product exists
    cursor.execute("SELECT product_id FROM products WHERE product_id=%s", (product_id,))
    if not cursor.fetchone():
        cursor.close()
        db.close()
        return jsonify({'message': 'Product not found'}), 404

    # Check if already in cart
    cursor.execute("""
        SELECT id, quantity FROM cart_items
        WHERE user_id=%s AND product_id=%s
    """, (user_id, product_id))
    item = cursor.fetchone()

    if item:
        cursor.execute(
            "UPDATE cart_items SET quantity=%s WHERE id=%s",
            (item['quantity'] + 1, item['id'])
        )
    else:
        cursor.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (%s,%s,1)",
            (user_id, product_id)
        )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({'message': 'Added to cart'})


@app.route('/add_to_cart')
def add_to_cart():
    if 'user_id' not in session:
        flash('Please login to view your cart')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Connect to MySQL
    
    # cursor = db.cursor(dictionary=True)
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Fetch cart items for this user, joining with product info
    cursor.execute("""
        SELECT c.id AS cart_id, p.product_id, p.product_name, p.price, c.quantity
        FROM cart_items c
        JOIN products p ON c.product_id = p.product_id
        WHERE c.user_id = %s
    """, (user_id,))
    cart_items = cursor.fetchall()

    db.commit()
    cursor.close()
    db.close()

    return render_template('add_to_cart.html', cart_items=cart_items)




if __name__ == '__main__':
    app.run(debug=True)
