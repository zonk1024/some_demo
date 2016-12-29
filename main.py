#!/usr/bin/env python

import flask
import redis
import random
import hashlib


r = redis.Redis('192.168.99.100')

app = flask.Flask(__name__)
app.debug = True

BUTTON_TEMPLATE = '''<input value="value1" type="button" hidden_attr="#{0}" class="hidden_value_class" style="background-color: #{0}" />
            <br />
'''

THE_UPPER_PAGE = '''
<html>
    <head>
    <title>This is like some kind of real page or something</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
    <body>
        <form>'''

THE_LOWER_PAGE = '''
        </form>
    </body>
    <script type="text/javascript">
    $(document).on('click', '.hidden_value_class', function(event) {
        var hidden_attr = $(event.target).attr('hidden_attr');
        $('body').css('background-color', hidden_attr);
    });
    </script>
</html>
'''

def new_random_string():
    return hashlib.sha1(str(random.random())).hexdigest()


def is_logged_in():
    cookie = flask.request.headers.get('Cookie')
    if not cookie:
        return False
    return r.exists('cookie:{}'.format(cookie))


@app.route('/')
def index():
    if not is_logged_in():
        return flask.redirect('/login')
    buttons = []
    for r in range(4):
        for g in range(4):
            for b in range(4):
                buttons.append(BUTTON_TEMPLATE.format("{}{}{}".format(
                    hex(r * 64)[2:].zfill(2),
                    hex(g * 64)[2:].zfill(2),
                    hex(b * 64)[2:].zfill(2),
                )))
    response = flask.Response("{}{}{}".format(
        THE_UPPER_PAGE,
        '\n'.join(buttons),
        THE_LOWER_PAGE,
    ))
    return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        username = flask.request.form['username']
        password = flask.request.form['password']
        if username == 'bob' and password == 'bobpass':
            random_value = new_random_string()
            r.setex('cookie:{}'.format(random_value), 1, 30)
            response = flask.Response('Logged in!')
            # TODO: Verify this is correct -- appears to work though
            response.headers['Set-Cookie'] = random_value
            return response
        else:
            return 'Bad username/password!'
    return '<html><body><form method="POST">Username: <input type="text" name="username" /><br />Password: <input type="password" name="password" /><br /><input type="submit" value="send it" /></form></body></html>'


@app.route('/test')
def test_endpoint():
    return repr(flask.request.headers)


if __name__ == '__main__':
    app.run()
