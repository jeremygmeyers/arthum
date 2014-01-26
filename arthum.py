# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash

from contextlib import closing

# configuration
DATABASE = '/tmp/arthum.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_quiz():
    
    cur = g.db.execute('select title, artist, link, year, id from images order by RANDOM() limit 1')
    entries = [dict(title=row[0], artist=row[1], link=row[2], year=row[3], id_entry=row[4]) for row in cur.fetchall()]
    return render_template('show_quiz.html', entries=entries)

@app.route('/show')
def show_entries():
    cur = g.db.execute('select title, artist, link, year, id from images order by id desc')
    entries = [dict(title=row[0], artist=row[1], link=row[2], year=row[3], id_entry=row[4]) for row in cur.fetchall()]
    cur2 = g.db.execute('select title, artist, year, description, imageID from answers order by id desc')
    answers = [dict(title=row[0], artist=row[1], year=row[2], description=row[3], imageID=row[4]) for row in cur2.fetchall()]
    return render_template('show_entries.html', entries=entries, answers=answers)

@app.route('/delete', methods=['POST'])
def delete_entry():
    if not session.get('logged_in'):
        abort(401)
    imageID = request.form['delete_entry']
    g.db.execute('delete from images where id=?', imageID)
    g.db.commit()
    flash('entry was successfully deleted')
    return redirect(url_for('show_entries'))

@app.route('/answer', methods=['POST'])
def answer():
    g.db.execute('insert into answers (imageID, title, artist, year, description) values (?, ?, ?, ?, ?)',
        [request.form['imageID'], request.form['title'], request.form['artist'], request.form['year'], request.form['description']])
    g.db.commit()
    flash('Your answer: ' + request.form['title'] + ' by ' + request.form['artist'] + ' in ' + request.form['year'] + '<br> Your description: ' + request.form['description'])
    imageID = request.form['imageID']
    cur = g.db.execute('select title, artist, link, year from images where id=?', (imageID,))

    [flash('Recorded answer: ' + row[0] + ' by ' + row[1] + ' in ' + str(row[3])) for row in cur.fetchall()]

    return render_template('show_quiz.html')

@app.route('/add_entry')
def add_entries():
    return render_template('add_entry.html')

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into images (title, artist, link, year) values (?, ?, ?, ?)',
                 [request.form['title'], request.form['artist'], request.form['link'], request.form['year']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    app.run()

