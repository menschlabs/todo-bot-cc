"""
Flask Documentation:     http://flask.pocoo.org/docs/
Flask-SQLAlchemy Documentation: http://flask-sqlalchemy.pocoo.org/
SQLAlchemy Documentation: http://docs.sqlalchemy.org/
FB Messenger Platform docs: https://developers.facebook.com/docs/messenger-platform.

This file creates your application.
"""

import os

import messages
import flask
import requests
from flask_sqlalchemy import SQLAlchemy
import pprint
import json

FACEBOOK_API_MESSAGE_SEND_URL = (
    'https://graph.facebook.com/v2.6/me/messages?access_token=%s')
FACEBOOK_APP_URL = ('https://graph.facebook.com/app?access_token=%s')
FACEBOOK_APP_ID = '723638517839355'

app = flask.Flask(__name__)

# TODO: Set environment variables appropriately.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FACEBOOK_PAGE_ACCESS_TOKEN'] = os.environ[
    'FACEBOOK_PAGE_ACCESS_TOKEN']
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')
app.config['FACEBOOK_WEBHOOK_VERIFY_TOKEN'] = 'mysecretverifytoken'


db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(80), unique=True)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    todo = db.Column(db.String, nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User', backref='todo')


"""class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Free form address for simplicity.
    full_address = db.Column(db.String, nullable=False)

    # Connect each address to exactly one user.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    # This adds an attribute 'user' to each address, and an attribute
    # 'addresses' (containing a list of addresses) to each user.
    user = db.relationship('User', backref='addresses')"""


@app.route('/')
def index():
    """Simple example handler.

    This is just an example handler that demonstrates the basics of SQLAlchemy,
    relationships, and template rendering in Flask.

    """
    # Just for demonstration purposes
    for user in User.query:  #
        print 'User %d, userid %s' % (user.id, user.userid)
        for todo in user.todo:
            print 'Todo %s' % (todo.todo)

    # Render all of this into an HTML template and return it. We use
    # User.query.all() to obtain a list of all users, rather than an
    # iterator. This isn't strictly necessary, but just to illustrate that both
    # User.query and User.query.all() are both possible options to iterate over
    # query results.
    return flask.render_template('index.html', users=User.query.all())


@app.route('/fb_webhook', methods=['GET', 'POST'])
def fb_webhook():
    """This handler deals with incoming Facebook Messages.

    In this example implementation, we handle the initial handshake mechanism,
    then just echo all incoming messages back to the sender. Not exactly Skynet
    level AI, but we had to keep it short...

    """
    # Handle the initial handshake request.
    if flask.request.method == 'GET':
        if (flask.request.args.get('hub.mode') == 'subscribe' and
            flask.request.args.get('hub.verify_token') ==
            app.config['FACEBOOK_WEBHOOK_VERIFY_TOKEN']):
            challenge = flask.request.args.get('hub.challenge')
            return challenge
        else:
            print 'Received invalid GET request'
            return ''  # Still return a 200, otherwise FB gets upset.

    # Get the request body as a dict, parsed from JSON.
    payload = flask.request.json

    pprint.pprint(payload)
    app_url = FACEBOOK_APP_URL % (app.config['FACEBOOK_PAGE_ACCESS_TOKEN'])
    app_data = json.loads(requests.get(app_url).content)
    if app_data['id'] != FACEBOOK_APP_ID:
        return ''

    # TODO: Validate app ID and other parts of the payload to make sure we're
    # not accidentally processing data that wasn't intended for us.

    # Handle an incoming message.
    # TODO: Improve error handling in case of unexpected payloads.
    try:
        if(payload['object'] == 'page' and payload['entry']):
            for entry in payload['entry']:
                for event in entry['messaging']:
                    if 'message' not in event:
                        continue
                    message = event['message']
                    sender = event['sender']['id']
                    print sender
                    # Ignore messages sent by us.
                    if message.get('is_echo', False):
                        continue
                    # Ignore messages with non-text content.
                    if 'text' not in message:
                        continue
                    sender_id = event['sender']['id']
                    request_url = FACEBOOK_API_MESSAGE_SEND_URL % (
                        app.config['FACEBOOK_PAGE_ACCESS_TOKEN'])
                    message_text = messages.processMessage(message['text'],
                                                           sender)
                    if not message_text:
                        message_text = "Sorry did not get you..."
                    requests.post(request_url,
                                  headers={'Content-Type': 'application/json'},
                                  json={'recipient': {'id': sender_id},
                                        'message': {'text': message_text}})

        # Return an empty response.
        return ''
    except:
        requests.post(request_url,
                      headers={'Content-Type': 'application/json'},
                      json={'recipient': {'id': sender_id},
                            'message': {'text': "Something Happened"}})


if __name__ == '__main__':
    app.run(debug=True)
