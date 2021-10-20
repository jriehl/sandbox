'''Web application for A Network of Ideas.
'''

from flask import Flask, redirect, url_for
from markupsafe import escape

app = Flask(__name__)


@app.route('/')
def home():
    return redirect(url_for('viewer', title='index'))


@app.route('/edit/<title>')
def editor(title):
    # TODO
    return f'<h1>Edit "{escape(title)}"...</h1>'


@app.route('/<title>')
def viewer(title):
    # TODO
    return f'''<h1>{escape(title)}</h1>
<a href='{url_for('editor', title=title)}'>Edit...</a>
'''
