import os

from flask import Flask, request, jsonify
from rivescript import RiveScript

bot = RiveScript()
bot.load_directory(os.path.join(os.path.dirname(__file__), 'brain'))
bot.sort_replies()

app = Flask(__name__)

@app.route('/reply', methods=['POST'])
def reply():
    result = {
        'status': 'error',
        'error': 'The developer is too lazy to cover this code path.'
    }
    params = request.json
    if not params:
        result['error'] = 'Request must be of the application/json type.'
    else:
        username = params.get('username', 'anonymous')
        message = params.get('message')
        uservars = params.get('uservars', dict())
        if message is None:
            result['error'] = 'The message field is a required input.'
        else:
            if type(uservars) is dict:
                for key, value in uservars.items():
                    bot.set_uservar(username, key, value)
            result = {
                'status': 'ok',
                'reply': bot.reply(username, message),
                'vars': bot.get_uservars(username)
            }
    return jsonify(result)

@app.route('/')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
