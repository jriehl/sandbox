'''Web application for A Network of Ideas.
'''

import functools

from flask import Flask, redirect, url_for
from werkzeug.exceptions import NotFound
from markupsafe import escape

from . import anoi, wordnet as wn


NIL = anoi.ANOIReserved.NIL.value


app = Flask(__name__)


class ANOIFacade:
    def __init__(self, space_cls, *args, **kws):
        if not issubclass(space_cls, anoi.ANOISpace):
            raise TypeError(f'{space_cls} is not a subtype of ANOISpace')
        self.space = space_cls(*args, **kws)
        self.namespace = anoi.ANOINamespace(self.space, 'wordnet')
        self.name_uid = self.namespace.basis.get_name('NAME')
        self.loader = wn.ANOIWordNetLoader(self.namespace, True)
        if not self.loader.loaded:
            self.loader.load()

    @functools.lru_cache(maxsize=65536)
    def uid_to_html(self, uid):
        valid = self.space.is_valid(uid)
        if uid < 0x110000 and (char := chr(uid)).isprintable():
            uid_str = f'{char}'
        elif uid in anoi.ANOIReservedSet:
            reserved = anoi.ANOIReserved(uid)
            uid_str = reserved.name
        elif valid and (name := self.space.cross(uid, self.name_uid)) != NIL:
            uid_str = anoi.vec_to_str(self.space.get_content(name))
        else:
            uid_str = hex(uid)
        return f'<a href="{hex(uid)}">{uid_str}</a>' if valid else uid_str


@functools.cache
def get_facade(space_cls = anoi.ANOIInMemorySpace, *args, **kws):
    return ANOIFacade(space_cls, *args, **kws)


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


@app.route('/nav/<uid>')
def nav(uid: str):
    try:
        if uid.startswith('0x'):
            uid = int(uid[2:], 16)
        else:
            uid = int(uid)
    except ValueError:
        raise NotFound()
    facade = get_facade()
    uid_to_html = facade.uid_to_html
    space = facade.space
    if not space.is_valid(uid):
        raise NotFound()
    iter_0 = ((uid_to_html(key), uid_to_html(space.cross(uid, key)))
        for key in sorted(space.get_keys(uid)))
    nav_iter = ((key if len(key) > 1 else f'"{key}"', value)
        for key, value in iter_0)
    navbar = ''.join(f'<li>{key} : {value}</li>' for key, value in nav_iter)
    contents = ''.join(facade.uid_to_html(child)
        for child in space.get_content(uid))
    title = f'UID {uid} ({hex(uid)})'
    return f'''<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
  </head>
  <body>
    <h1>{title}</h1>
    <ul>{navbar}</ul>
    <p>{contents}</p>
  </body>
</html>
'''
