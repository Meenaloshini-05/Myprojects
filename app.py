from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "mysecret123"  # keep this secret in production

DB_PATH = 'expense.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT,
            password TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            date TEXT,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

create_tables()

# ---------- Auth routes ----------
@app.route('/')
def index():
    return redirect('/login')

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form.get('email','').strip()
        password = request.form['password'].strip()
        if not username or not password:
            flash("Username and password required.", "danger")
            return redirect('/signup')
        hashed = generate_password_hash(password)
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users(username,email,password) VALUES (?,?,?)',
                         (username,email,hashed))
            conn.commit()
            conn.close()
            flash("Signup successful. Please login.", "success")
            return redirect('/login')
        except sqlite3.IntegrityError:
            conn.close()
            flash("Username already exists.", "danger")
            return redirect('/signup')
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully.", "success")
            return redirect('/dashboard')
        flash("Invalid username or password.", "danger")
        return redirect('/login')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect('/login')

# ---------- Expense routes ----------
def parse_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None

@app.route('/add_expense', methods=['GET','POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
        except:
            flash("Invalid amount.", "danger")
            return redirect('/add_expense')
        category = request.form['category'].strip()
        date_str = request.form['date']
        description = request.form.get('description','').strip()
        if not date_str:
            date_str = date.today().isoformat()
        user_id = session['user_id']
        conn = get_db_connection()
        conn.execute('INSERT INTO expenses (user_id,amount,category,date,description) VALUES (?,?,?,?,?)',
                     (user_id, amount, category, date_str, description))
        conn.commit()
        conn.close()
        flash("Expense added.", "success")
        return redirect('/dashboard')
    return render_template('add_expense.html')

@app.route('/edit_expense/<int:exp_id>', methods=['GET','POST'])
def edit_expense(exp_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db_connection()
    expense = conn.execute('SELECT * FROM expenses WHERE id=? AND user_id=?', (exp_id, user_id)).fetchone()
    if not expense:
        conn.close()
        flash("Expense not found.", "danger")
        return redirect('/dashboard')
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
        except:
            flash("Invalid amount.", "danger")
            return redirect(url_for('edit_expense', exp_id=exp_id))
        category = request.form['category'].strip()
        date_str = request.form['date']
        description = request.form.get('description','').strip()
        conn.execute('UPDATE expenses SET amount=?, category=?, date=?, description=? WHERE id=? AND user_id=?',
                     (amount, category, date_str, description, exp_id, user_id))
        conn.commit()
        conn.close()
        flash("Expense updated.", "success")
        return redirect('/dashboard')
    conn.close()
    return render_template('edit_expense.html', exp=expense)

@app.route('/delete_expense/<int:exp_id>', methods=['POST'])
def delete_expense(exp_id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id=? AND user_id=?', (exp_id, user_id))
    conn.commit()
    conn.close()
    flash("Expense deleted.", "info")
    return redirect('/dashboard')

# ---------- Dashboard, filtering and summaries ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']

    # Filters from querystring
    start = request.args.get('start_date','').strip()
    end = request.args.get('end_date','').strip()
    category = request.args.get('category','').strip()

    q = 'SELECT * FROM expenses WHERE user_id=?'
    params = [user_id]

    if start:
        q += ' AND date >= ?'
        params.append(start)
    if end:
        q += ' AND date <= ?'
        params.append(end)
    if category:
        q += ' AND category = ?'
        params.append(category)

    q += ' ORDER BY date DESC'

    conn = get_db_connection()
    expenses = conn.execute(q, params).fetchall()

    # Totals
    total_all = sum([row['amount'] for row in expenses])
    today_str = date.today().isoformat()
    total_today = conn.execute('SELECT SUM(amount) as s FROM expenses WHERE user_id=? AND date=?', (user_id, today_str)).fetchone()['s'] or 0
    # current month
    month_prefix = date.today().strftime("%Y-%m")
    total_month = conn.execute('SELECT SUM(amount) as s FROM expenses WHERE user_id=? AND date LIKE ?', (user_id, month_prefix + '%')).fetchone()['s'] or 0

    # Category breakdown (for chart)
    categories = {}
    for exp in expenses:
        categories[exp['category']] = categories.get(exp['category'], 0) + exp['amount']

    # Monthly totals for bar chart (last 6 months)
    monthly = {}
    for i in range(0,6):
        dt = date.today().replace(day=1)
        # subtract months
        month = (dt.month - i - 1) % 12 + 1
        year = dt.year - ((dt.month - i - 1)//12)
        key = f"{year}-{month:02d}"
        monthly[key] = 0.0
    rows = conn.execute("SELECT date, amount FROM expenses WHERE user_id=? ORDER BY date DESC", (user_id,)).fetchall()
    for r in rows:
        d = parse_date(r['date'])
        if not d: 
            continue
        key = f"{d.year}-{d.month:02d}"
        if key in monthly:
            monthly[key] += r['amount']

    conn.close()

    # Pass values to template
    return render_template('dashboard.html',
                           expenses=expenses,
                           chart_data=json.dumps(categories),
                           monthly_data=json.dumps(monthly),
                           total_all=total_all,
                           total_today=total_today,
                           total_month=total_month,
                           filters={'start':start,'end':end,'category':category})

# ---------- run ----------
if __name__ == '__main__':
    app.run(debug=True)
