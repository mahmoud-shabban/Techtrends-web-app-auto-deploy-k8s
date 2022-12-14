from crypt import methods
from fileinput import filename
import logging
import mimetypes
import sqlite3
from telnetlib import STATUS
from urllib import response
import json


from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
db_connetion_count = 0
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connetion_count
    db_connetion_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

# implementing health check
@app.route('/healthz', methods = ['GET'])
def health():
    try:
        conn = get_db_connection()
        # there is connection testing posts table
        test = conn.execute('select * from posts').fetchall()
        if test:
            response = app.response_class(
        response = json.dumps({"status": "OK, healthy"}),
        status = 200,
        mimetype= 'application/json'
        )
            return response
        else:
            response = app.response_class(
        response = json.dumps({"Error": "Unhealthy"}),
        status = 500,
        mimetype= 'application/json'
        )
        return response
    # if there is no connection
    except:

        response = app.response_class(
        response = json.dumps({"Error": "Unhealthy"}),
        status = 500,
        mimetype= 'application/json'
    )
        return response

# query the db for the number of posts
def query():
    with get_db_connection() as con:
        n_posts = con.execute('select count(*) as count from posts').fetchall()
    return n_posts[0]['count']

# metrics implementation
@app.route('/metrics', methods=['GET'])
def metric():
    response = app.response_class(
        response = json.dumps({'post_count':query(), 'db_connetion_count': db_connetion_count}),
        status= 200,
        mimetype= 'application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename= 'app.log', level= logging.DEBUG, )
   app.run(host='0.0.0.0', port='3111')
