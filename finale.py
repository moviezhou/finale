# -*- coding: utf-8 -*-

import sqlite3
import random
from contextlib import closing
from hashlib import md5
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

# configuration
DATABASE = '/home/moviezhou/PycharmProjects/finale/db/finale.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def draw():
    return render_template('draw_question.html')
@app.route('/manage')
def show_entries():
    if not session.get('logged_in'):
        abort('401')
    cur = g.db.execute('select title, text, required, category from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], required=row[2], category=row[3]) for row in cur.fetchall()]
    return render_template('manage.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort('401')
    if request.form['title'] and request.form['text']:
        if request.form['required'] == 'T':
            g.db.execute('insert into required (title, text, required, category) values (?, ?, ?, ?) '
                     , [request.form['title'], request.form['text'], request.form['required'],
                        request.form['category']])
        else:
            g.db.execute('insert into entries (title, text, required, category) values (?, ?, ?, ?) '
                     , [request.form['title'], request.form['text'],request.form['required'],
                        request.form['category']])
        g.db.commit()
        flash(u'题目添加成功')
        return redirect(url_for('show_entries'))
    else:
        flash(u'题目或内容不能为空')
        return redirect(url_for('show_entries'))


@app.route('/draw', methods=['GET'])
def drawquestion():
    # required questions query result
    req_result = query_db('select title, text from required')[0]
    question_req = [dict(title=req_result['title'], text=req_result['text'])]


    cur = g.db.execute('select id from entries where category="A"')
    entries_a = [row[0] for row in cur.fetchall()]
    entries_a_count = len(entries_a)
    cur = g.db.execute('select id from entries where category="B"')
    entries_b = [row[0] for row in cur.fetchall()]
    entries_b_count = len(entries_b)

    if entries_a_count > 1 and entries_b_count >1:
        rand_a = random.randint(0, entries_a_count - 1)  # zero index
        rand_b = random.randint(0, entries_b_count - 1)
        print(rand_a, rand_b)
        # random questions query result
        rand_result = query_db('select title, text, category from entries where id = ?', [entries_a[rand_a]], one=True)
        question_a = [dict(title=rand_result['title'], text=rand_result['text'])]
        # questions.append(question_a)
        rand_result = query_db('select title, text, category from entries where id = ?', [entries_b[rand_b]], one=True)
        question_b = [dict(title=rand_result['title'], text=rand_result['text'])]
        # questions.append(question_b)
        return render_template('random.html', entries = question_req + question_a + question_b)
    else:
        abort('404')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        cur = g.db.execute('select username, password from users where username = ? and password = ?',
                           [request.form['username'], md5(request.form['password']).hexdigest()])
        res = cur.fetchall()
        if res:
            if res[0][0] != request.form['username']:
                error = 'Invalid username.'
            elif res[0][1] != md5(request.form['password']).hexdigest():
                error = 'Invalid password.'
            else:
                session['logged_in'] = True
                flash(u'登录成功')
                return redirect(url_for('show_entries'))
        else:
            error = 'User doesn\'t exists.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'退出系统')
    return redirect(url_for('draw'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        if len(request.form['username']) < 5:
            error = 'Invalid username, at least 5 characters.'
        elif len(request.form['password']) < 6:
            error = 'Invalid password, at least 6 characters'
        else:
            g.db.execute('insert into users (username, password) values (?, ?)',
                         [request.form['username'], md5(request.form['password']).hexdigest()])
            g.db.commit()
            flash(u'注册成功')
            return redirect(url_for('show_entries'))
    return render_template('signup.html', error=error)


if __name__ == '__main__':
    app.run()
