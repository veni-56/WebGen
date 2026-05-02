"""Patch generator.py: replace old single-vendor ecom helpers with multi-vendor ones."""
import re

with open('generator.py', encoding='utf-8') as f:
    content = f.read()

# ── Find the old body start (after the docstring we already patched) ──────────
# The old body starts right after the triple-quote docstring of _mv_app_py
# and ends just before the section-4 comment block.

START = '\nimport os\nimport sqlite3\nfrom flask import (Flask, render_template, request, redirect,\n                   url_for, session, flash)\nfrom werkzeug.security import generate_password_hash, check_password_hash\nfrom werkzeug.utils import secure_filename\n\napp = Flask(__name__)\napp.secret_key = os.environ.get(\'SECRET_KEY\', \'change-this-in-production\')'

END_MARKER = "\n\n# ─────────────────────────────────────────────────────────────────────────────\n# 4. SHARED CSS / JS\n# ─────────────────────────────────────────────────────────────────────────────"

si = content.find(START)
ei = content.find(END_MARKER, si)

if si == -1 or ei == -1:
    print(f"ERROR: markers not found. si={si} ei={ei}")
    exit(1)

print(f"Replacing chars {si}..{ei} ({ei-si} chars)")

NEW_BODY = r'''
import os
import sqlite3
import uuid
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production')

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
SELLER_SHARE   = 0.90
PLATFORM_SHARE = 0.10

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            category TEXT DEFAULT 'General',
            image TEXT DEFAULT 'default.png',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            total_price REAL NOT NULL,
            payment_ref TEXT,
            status TEXT DEFAULT 'paid',
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            seller_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS seller_earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_id INTEGER NOT NULL,
            order_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS platform_earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL UNIQUE,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    admin = conn.execute("SELECT id FROM users WHERE email='admin@marketplace.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
                     ('Admin','admin@marketplace.com',
                      generate_password_hash('admin123'),'admin'))
    conn.commit()
    conn.close()

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit('.',1)[1].lower()
        fn  = uuid.uuid4().hex + '.' + ext
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
        return fn
    return 'default.png'

def login_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if 'user_id' not in session:
            flash('Please login first.','warning')
            return redirect(url_for('login'))
        return f(*a,**kw)
    return dec

def seller_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if session.get('role') not in ('seller','admin'):
            flash('Seller access required.','error')
            return redirect(url_for('index'))
        return f(*a,**kw)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*a,**kw):
        if session.get('role') != 'admin':
            flash('Admin access required.','error')
            return redirect(url_for('index'))
        return f(*a,**kw)
    return dec

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name  = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        pw    = generate_password_hash(request.form['password'])
        role  = request.form.get('role','customer')
        if role not in ('seller','customer'): role = 'customer'
        try:
            conn = get_db()
            conn.execute('INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)',(name,email,pw,role))
            conn.commit(); conn.close()
            flash('Account created! Please login.','success')
            return redirect(url_for('login'))
        except Exception:
            flash('Email already registered.','error')
    return render_template('auth/signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        pw    = request.form['password']
        conn  = get_db()
        user  = conn.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], pw):
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            session['role']      = user['role']
            if user['role'] == 'admin':   return redirect(url_for('admin_dashboard'))
            if user['role'] == 'seller':  return redirect(url_for('seller_dashboard'))
            return redirect(url_for('index'))
        flash('Invalid email or password.','error')
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    q=request.args.get('q','').strip(); cat=request.args.get('category','')
    minp=request.args.get('min_price',''); maxp=request.args.get('max_price','')
    sort=request.args.get('sort','newest')
    conn=get_db()
    sql='SELECT p.*,u.name as seller_name FROM products p JOIN users u ON p.seller_id=u.id WHERE p.stock>0'
    args=[]
    if q:    sql+=' AND p.name LIKE ?';  args.append(f'%{q}%')
    if cat:  sql+=' AND p.category=?';   args.append(cat)
    if minp: sql+=' AND p.price>=?';     args.append(float(minp))
    if maxp: sql+=' AND p.price<=?';     args.append(float(maxp))
    sql+=({'price_asc':' ORDER BY p.price ASC','price_desc':' ORDER BY p.price DESC'}).get(sort,' ORDER BY p.created_at DESC')
    products=conn.execute(sql,args).fetchall()
    categories=[r[0] for r in conn.execute('SELECT DISTINCT category FROM products').fetchall()]
    conn.close()
    return render_template('customer/index.html',products=products,categories=categories,
                           q=q,selected_cat=cat,min_price=minp,max_price=maxp,sort=sort)

@app.route('/product/<int:pid>')
def product_detail(pid):
    conn=get_db()
    p=conn.execute('SELECT p.*,u.name as seller_name FROM products p JOIN users u ON p.seller_id=u.id WHERE p.id=?',(pid,)).fetchone()
    related=conn.execute('SELECT * FROM products WHERE category=? AND id!=? AND stock>0 LIMIT 4',(p['category'],pid)).fetchall() if p else []
    conn.close()
    if not p: return render_template('errors/404.html'),404
    return render_template('customer/product.html',product=p,related=related)

@app.route('/cart')
@login_required
def cart():
    conn=get_db()
    items=conn.execute('''SELECT ci.id,ci.quantity,p.name,p.price,p.image,p.stock,p.id as pid
                          FROM cart_items ci JOIN products p ON ci.product_id=p.id WHERE ci.user_id=?''',(session['user_id'],)).fetchall()
    total=sum(i['price']*i['quantity'] for i in items)
    conn.close()
    return render_template('customer/cart.html',items=items,total=total)

@app.route('/cart/add/<int:pid>',methods=['POST'])
@login_required
def add_to_cart(pid):
    qty=max(1,int(request.form.get('quantity',1)))
    conn=get_db()
    p=conn.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
    if not p or p['stock']<1:
        flash('Product unavailable.','error'); conn.close(); return redirect(url_for('index'))
    ex=conn.execute('SELECT * FROM cart_items WHERE user_id=? AND product_id=?',(session['user_id'],pid)).fetchone()
    if ex: conn.execute('UPDATE cart_items SET quantity=? WHERE id=?',(min(ex['quantity']+qty,p['stock']),ex['id']))
    else:  conn.execute('INSERT INTO cart_items (user_id,product_id,quantity) VALUES (?,?,?)',(session['user_id'],pid,min(qty,p['stock'])))
    conn.commit(); conn.close()
    flash(f'"{p["name"]}" added to cart.','success')
    return redirect(request.referrer or url_for('cart'))

@app.route('/cart/update/<int:iid>',methods=['POST'])
@login_required
def update_cart(iid):
    qty=int(request.form.get('quantity',1)); conn=get_db()
    if qty<1: conn.execute('DELETE FROM cart_items WHERE id=? AND user_id=?',(iid,session['user_id']))
    else:     conn.execute('UPDATE cart_items SET quantity=? WHERE id=? AND user_id=?',(qty,iid,session['user_id']))
    conn.commit(); conn.close()
    return redirect(url_for('cart'))

@app.route('/cart/remove/<int:iid>',methods=['POST'])
@login_required
def remove_from_cart(iid):
    conn=get_db()
    conn.execute('DELETE FROM cart_items WHERE id=? AND user_id=?',(iid,session['user_id']))
    conn.commit(); conn.close()
    flash('Item removed.','info')
    return redirect(url_for('cart'))

@app.route('/checkout',methods=['GET','POST'])
@login_required
def checkout():
    conn=get_db()
    items=conn.execute('''SELECT ci.id,ci.quantity,p.id as pid,p.name,p.price,p.stock,p.seller_id
                          FROM cart_items ci JOIN products p ON ci.product_id=p.id WHERE ci.user_id=?''',(session['user_id'],)).fetchall()
    if not items:
        flash('Your cart is empty.','warning'); conn.close(); return redirect(url_for('cart'))
    total=sum(i['price']*i['quantity'] for i in items)
    if request.method=='POST':
        address=request.form.get('address','').strip()
        if not address:
            flash('Please enter a delivery address.','error'); conn.close(); return redirect(url_for('checkout'))
        ref='PAY-'+uuid.uuid4().hex[:10].upper()
        conn.execute('INSERT INTO orders (customer_id,total_price,payment_ref,status,address) VALUES (?,?,?,?,?)',
                     (session['user_id'],total,ref,'paid',address))
        oid=conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        seller_totals={}
        for i in items:
            conn.execute('INSERT INTO order_items (order_id,product_id,seller_id,quantity,price) VALUES (?,?,?,?,?)',
                         (oid,i['pid'],i['seller_id'],i['quantity'],i['price']))
            conn.execute('UPDATE products SET stock=MAX(0,stock-?) WHERE id=?',(i['quantity'],i['pid']))
            seller_totals[i['seller_id']]=seller_totals.get(i['seller_id'],0)+i['price']*i['quantity']
        for sid,amt in seller_totals.items():
            conn.execute('INSERT INTO seller_earnings (seller_id,order_id,amount) VALUES (?,?,?)',
                         (sid,oid,round(amt*SELLER_SHARE,2)))
        conn.execute('INSERT INTO platform_earnings (order_id,amount) VALUES (?,?)',(oid,round(total*PLATFORM_SHARE,2)))
        conn.execute('DELETE FROM cart_items WHERE user_id=?',(session['user_id'],))
        conn.commit(); conn.close()
        flash(f'Order placed! Ref: {ref}','success')
        return redirect(url_for('order_detail',oid=oid))
    conn.close()
    return render_template('customer/checkout.html',items=items,total=total)

@app.route('/orders')
@login_required
def my_orders():
    conn=get_db()
    orders=conn.execute('SELECT * FROM orders WHERE customer_id=? ORDER BY created_at DESC',(session['user_id'],)).fetchall()
    conn.close()
    return render_template('customer/orders.html',orders=orders)

@app.route('/orders/<int:oid>')
@login_required
def order_detail(oid):
    conn=get_db()
    order=conn.execute('SELECT * FROM orders WHERE id=?',(oid,)).fetchone()
    items=conn.execute('''SELECT oi.*,p.name,p.image FROM order_items oi
                          JOIN products p ON oi.product_id=p.id WHERE oi.order_id=?''',(oid,)).fetchall()
    conn.close()
    if not order or (order['customer_id']!=session['user_id'] and session.get('role')!='admin'):
        return render_template('errors/403.html'),403
    return render_template('customer/order_detail.html',order=order,items=items)

@app.route('/seller/dashboard')
@login_required
@seller_required
def seller_dashboard():
    conn=get_db()
    products=conn.execute('SELECT * FROM products WHERE seller_id=? ORDER BY created_at DESC',(session['user_id'],)).fetchall()
    total_earned=conn.execute('SELECT COALESCE(SUM(amount),0) FROM seller_earnings WHERE seller_id=?',(session['user_id'],)).fetchone()[0]
    total_orders=conn.execute('SELECT COUNT(DISTINCT order_id) FROM seller_earnings WHERE seller_id=?',(session['user_id'],)).fetchone()[0]
    recent=conn.execute('''SELECT o.id,o.created_at,o.status,o.total_price,u.name as customer_name
                           FROM orders o JOIN users u ON o.customer_id=u.id
                           WHERE o.id IN (SELECT DISTINCT order_id FROM order_items WHERE seller_id=?)
                           ORDER BY o.created_at DESC LIMIT 5''',(session['user_id'],)).fetchall()
    conn.close()
    return render_template('seller/dashboard.html',products=products,
                           total_earned=total_earned,total_orders=total_orders,recent=recent)

@app.route('/seller/product/add',methods=['GET','POST'])
@login_required
@seller_required
def seller_add_product():
    cats=['Fashion','Electronics','Home & Kitchen','Beauty','Sports','Books','Toys','General']
    if request.method=='POST':
        img=save_image(request.files.get('image'))
        conn=get_db()
        conn.execute('INSERT INTO products (seller_id,name,description,price,stock,category,image) VALUES (?,?,?,?,?,?,?)',
                     (session['user_id'],request.form['name'].strip(),request.form.get('description','').strip(),
                      float(request.form['price']),int(request.form['stock']),request.form.get('category','General'),img))
        conn.commit(); conn.close()
        flash('Product added!','success')
        return redirect(url_for('seller_dashboard'))
    return render_template('seller/product_form.html',product=None,categories=cats)

@app.route('/seller/product/<int:pid>/edit',methods=['GET','POST'])
@login_required
@seller_required
def seller_edit_product(pid):
    cats=['Fashion','Electronics','Home & Kitchen','Beauty','Sports','Books','Toys','General']
    conn=get_db()
    p=conn.execute('SELECT * FROM products WHERE id=? AND seller_id=?',(pid,session['user_id'])).fetchone()
    if not p:
        conn.close(); flash('Product not found.','error'); return redirect(url_for('seller_dashboard'))
    if request.method=='POST':
        img=save_image(request.files.get('image'))
        if img=='default.png' and p['image']: img=p['image']
        conn.execute('UPDATE products SET name=?,description=?,price=?,stock=?,category=?,image=? WHERE id=?',
                     (request.form['name'].strip(),request.form.get('description','').strip(),
                      float(request.form['price']),int(request.form['stock']),
                      request.form.get('category','General'),img,pid))
        conn.commit(); conn.close()
        flash('Product updated!','success')
        return redirect(url_for('seller_dashboard'))
    conn.close()
    return render_template('seller/product_form.html',product=p,categories=cats)

@app.route('/seller/product/<int:pid>/delete',methods=['POST'])
@login_required
@seller_required
def seller_delete_product(pid):
    conn=get_db()
    conn.execute('DELETE FROM products WHERE id=? AND seller_id=?',(pid,session['user_id']))
    conn.commit(); conn.close()
    flash('Product deleted.','info')
    return redirect(url_for('seller_dashboard'))

@app.route('/seller/orders')
@login_required
@seller_required
def seller_orders():
    conn=get_db()
    orders=conn.execute('''SELECT DISTINCT o.*,u.name as customer_name FROM orders o
                           JOIN users u ON o.customer_id=u.id
                           WHERE o.id IN (SELECT DISTINCT order_id FROM order_items WHERE seller_id=?)
                           ORDER BY o.created_at DESC''',(session['user_id'],)).fetchall()
    pids=[r[0] for r in conn.execute('SELECT id FROM products WHERE seller_id=?',(session['user_id'],)).fetchall()]
    conn.close()
    return render_template('seller/orders.html',orders=orders,pids=pids)

@app.route('/seller/orders/<int:oid>/status',methods=['POST'])
@login_required
@seller_required
def seller_update_status(oid):
    conn=get_db()
    conn.execute('UPDATE orders SET status=? WHERE id=?',(request.form.get('status','pending'),oid))
    conn.commit(); conn.close()
    flash(f'Order updated.','success')
    return redirect(url_for('seller_orders'))

@app.route('/seller/earnings')
@login_required
@seller_required
def seller_earnings():
    conn=get_db()
    rows=conn.execute('''SELECT se.*,o.payment_ref,o.total_price,u.name as customer_name
                         FROM seller_earnings se JOIN orders o ON se.order_id=o.id
                         JOIN users u ON o.customer_id=u.id WHERE se.seller_id=?
                         ORDER BY se.created_at DESC''',(session['user_id'],)).fetchall()
    total=sum(r['amount'] for r in rows)
    conn.close()
    return render_template('seller/earnings.html',rows=rows,total=total)

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    conn=get_db()
    stats={
        'users':           conn.execute('SELECT COUNT(*) FROM users').fetchone()[0],
        'sellers':         conn.execute("SELECT COUNT(*) FROM users WHERE role='seller'").fetchone()[0],
        'products':        conn.execute('SELECT COUNT(*) FROM products').fetchone()[0],
        'orders':          conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0],
        'revenue':         conn.execute('SELECT COALESCE(SUM(total_price),0) FROM orders').fetchone()[0],
        'platform_income': conn.execute('SELECT COALESCE(SUM(amount),0) FROM platform_earnings').fetchone()[0],
        'seller_payouts':  conn.execute('SELECT COALESCE(SUM(amount),0) FROM seller_earnings').fetchone()[0],
    }
    recent=conn.execute('''SELECT o.*,u.name as customer_name FROM orders o
                           JOIN users u ON o.customer_id=u.id ORDER BY o.created_at DESC LIMIT 8''').fetchall()
    conn.close()
    return render_template('admin/dashboard.html',stats=stats,recent=recent)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    conn=get_db(); users=conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall(); conn.close()
    return render_template('admin/users.html',users=users)

@app.route('/admin/users/<int:uid>/delete',methods=['POST'])
@login_required
@admin_required
def admin_delete_user(uid):
    conn=get_db(); u=conn.execute('SELECT role FROM users WHERE id=?',(uid,)).fetchone()
    if u and u['role']=='admin': flash('Cannot delete admin.','error')
    else: conn.execute('DELETE FROM users WHERE id=?',(uid,)); conn.commit(); flash('User deleted.','info')
    conn.close(); return redirect(url_for('admin_users'))

@app.route('/admin/products')
@login_required
@admin_required
def admin_products():
    conn=get_db()
    products=conn.execute('SELECT p.*,u.name as seller_name FROM products p JOIN users u ON p.seller_id=u.id ORDER BY p.created_at DESC').fetchall()
    conn.close(); return render_template('admin/products.html',products=products)

@app.route('/admin/products/<int:pid>/delete',methods=['POST'])
@login_required
@admin_required
def admin_delete_product(pid):
    conn=get_db(); conn.execute('DELETE FROM products WHERE id=?',(pid,)); conn.commit(); conn.close()
    flash('Product deleted.','info'); return redirect(url_for('admin_products'))

@app.route('/admin/orders')
@login_required
@admin_required
def admin_orders():
    conn=get_db()
    orders=conn.execute('''SELECT o.*,u.name as customer_name FROM orders o
                           JOIN users u ON o.customer_id=u.id ORDER BY o.created_at DESC''').fetchall()
    conn.close(); return render_template('admin/orders.html',orders=orders)

@app.route('/admin/orders/<int:oid>/status',methods=['POST'])
@login_required
@admin_required
def admin_update_status(oid):
    conn=get_db(); conn.execute('UPDATE orders SET status=? WHERE id=?',(request.form['status'],oid)); conn.commit(); conn.close()
    flash(f'Order #{oid} updated.','success'); return redirect(url_for('admin_orders'))

@app.route('/admin/earnings')
@login_required
@admin_required
def admin_earnings():
    conn=get_db()
    rows=conn.execute('''SELECT pe.*,o.payment_ref,o.total_price,u.name as customer_name
                         FROM platform_earnings pe JOIN orders o ON pe.order_id=o.id
                         JOIN users u ON o.customer_id=u.id ORDER BY pe.created_at DESC''').fetchall()
    seller_summary=conn.execute('''SELECT u.name,u.email,COALESCE(SUM(se.amount),0) as total
                                   FROM users u LEFT JOIN seller_earnings se ON u.id=se.seller_id
                                   WHERE u.role='seller' GROUP BY u.id ORDER BY total DESC''').fetchall()
    total=sum(r['amount'] for r in rows); conn.close()
    return render_template('admin/earnings.html',rows=rows,total=total,seller_summary=seller_summary)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
'''
'''

content = content[:si] + NEW_BODY + content[ei:]
with open('generator.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done. File written.")
