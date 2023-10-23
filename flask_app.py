from flask import Flask
from flask import render_template, request, redirect, url_for, flash, session, abort
import sqlite3
from flask_session import Session

# Tworzenie aplikacji
app = Flask("Flask - Lab")

# Ścieżka do pliku bazy danych w sqlite
DATABASE = 'database.db'

# Tworzenie obsługi sesji
sess = Session()


@app.route('/create_database', methods=['GET', 'POST'])
def create_db():
    # Połączenie sie z bazą danych
    conn = sqlite3.connect(DATABASE)
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, is_admin BOOL)')
    # Stworzenie tabeli w bazie danych za pomocą sqlite3
    conn.execute('CREATE TABLE books (author TEXT, title TEXT)')
    # Zakończenie połączenia z bazą danych
    conn.close()

    return index()


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form['login']
    password = request.form['password']

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = ? AND password = ? AND is_admin = 1", (username, password,))
    user = cur.fetchone()

    if user:
        session['is_admin'] = True
    else:
        session['is_admin'] = False
    session['user'] = "username"
    return "Sesja została utworzona <br> <a href='/'> Dalej </a> "


@app.route('/logout', methods=['GET'])
def logout():
    # Jeżeli sesja klienta istnieje - usunięcie sesji
    if 'user' in session:
        session.pop('user')
    if 'is_admin' in session:
        session.pop('is_admin')
    else:
        # Przekierowanie klienta do strony początkowej
        redirect(url_for('index'))

    return "Wylogowano <br>  <a href='/'> Powrót </a>"


# Endpoint umożliwiający podanie parametru w postaci string'a
@app.route('/user/<username>')
def user_by_name(username):
    if session['is_admin']:
        con = sqlite3.connect(DATABASE)
        # Pobranie danych z tabeli
        cur = con.cursor()
        cur.execute("select * from users where username = ?", (username,))
        users = cur.fetchall()

        return render_template('t6.html', users=users)
    else:
        abort(403)

# Endpoint umożliwiający podanie parametru w postaci int'a
@app.route('/user/<int:user_id>')
def user_by_id(user_id):
    if session['is_admin']:
        con = sqlite3.connect(DATABASE)
        # Pobranie danych z tabeli
        cur = con.cursor()
        cur.execute("select * from users where id = ?", (user_id,))
        users = cur.fetchall()

        return render_template('t6.html', users=users)
    else:
        abort(403)

@app.route('/users', methods=['GET'])
def get_users():
    if session['is_admin']:
        con = sqlite3.connect(DATABASE)

        # Pobranie danych z tabeli
        cur = con.cursor()
        cur.execute("select * from users")
        users = cur.fetchall();

        return render_template('t4.html', users=users)
    else:
        abort(403)


@app.route('/', methods=['GET', 'POST'])
def index():
    con = sqlite3.connect(DATABASE)

    # Pobranie danych z tabeli
    cur = con.cursor()
    cur.execute("select * from books")
    books = cur.fetchall();

    # Sprawdzenie czy w sesji dla danego klienta zapisana jest nazwa użytkownika
    if 'user' in session:
        return render_template('t5.html', books=books)
    else:
        return render_template('t1.html')


@app.route('/add_user', methods=['POST'])
def add_user():
    login = request.form['login']
    password = request.form['password']
    admin = request.form['admin']

    # Dodanie użytkownika do bazy danych
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO users (username,password,is_admin) VALUES (?,?,?)", (login, password, admin))
    con.commit()
    con.close()

    return "Dodano użytkownika do bazy danych <br>" + get_users()


@app.route('/add_book', methods=['POST'])
def add_book():
    author = request.form['author']
    title = request.form['title']

    # Dodanie książki do bazy danych
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("INSERT INTO books (author,title) VALUES (?,?)", (author, title))
    con.commit()
    con.close()

    return "Dodano książkę do bazy danych <br>" + index()


# Uruchomienie aplikacji w trybie debug
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
sess.init_app(app)
app.config.from_object(__name__)
app.debug = True
app.run()
