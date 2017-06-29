"""
Flask Documentation:     http://flask.pocoo.org/docs/
Flask-SQLAlchemy Documentation: http://flask-sqlalchemy.pocoo.org/
SQLAlchemy Documentation: http://docs.sqlalchemy.org/
FB Messenger Platform docs: https://developers.facebook.com/docs/messenger-platform.

This file creates your application.
"""

import os

import random
from my_nlp import getFunctionality
import flask
import requests
from flask_sqlalchemy import SQLAlchemy
import pprint
import json
import datetime

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
    doneTime = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        nullable=False)
    user = db.relationship('User', backref='todo')


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
                    # Ignore messages sent by us.
                    if message.get('is_echo', False):
                        continue
                    # Ignore messages with non-text content.
                    if 'text' not in message:
                        continue
                    pprint.pprint(payload)
                    sender_id = event['sender']['id']
                    request_url = FACEBOOK_API_MESSAGE_SEND_URL % (
                        app.config['FACEBOOK_PAGE_ACCESS_TOKEN'])
                    requests.post(request_url,
                                  headers={'Content-Type': 'application/json'},
                                   json={"recipient":{"id":sender_id},
                                         "sender_action":"typing_on"})
                    message_json = processMessage(sender_id, message['text'])
                    requests.post(request_url,
                                  headers={'Content-Type': 'application/json'},
                                  json={'recipient': {'id': sender_id},
                                        'message': message_json})
    except:
        requests.post(request_url,
                      headers={'Content-Type': 'application/json'},
                       json={"recipient":{"id":sender_id},
                             'message': {'text': "Some internal error!"}})

    # Return an empty response.
    return ''


GREETINGS = ['Hello','Hi!','Hey!']


def greetings():
    return random.choice(GREETINGS)


def markDone(user, number):
    if user and number:
        todo = user.todo[number]
        todo.done = True
        todo.doneTime = str(datetime.datetime.now())
        db.session.add(todo)
        db.session.commit()
        return "Marked Todo: " + todo.todo + " as done!"
    else:
        return "Sorry did not get you...\nTry again"


def todoText(todo):
    if todo.done:
        return todo.doneTime
    else:
        return "Not marked as done"


def listAll(user=None, all=True, output=""):
    if user:
        elements = []
        if all:
            if len(user.todo) == 0:
                return "No Todos added\nAdd some on your own"
            for todo in user.todo:
                elements.append({"title": str(todo.id)+") "+todo.todo,
                                 "image_url":"",
                                 "subtitle":todoText(todo)})
        else:
            if len(user.todo) == 0:
                output += "No Todos added\n Add some on your own"
            for todo in user.todo:
                if todo.done:
                    elements.append({"title": todo.todo,
                                     "image_url":"",
                                     "subtitle":todoText(todo)})
            if len(output) == 0:
                output += "No Todos are marked done"
    else:
        output += "Application ran into some error"
    return {"attachment": {"type": "template",
                           "payload": {"template_type": "generic",
                                       "elements": elements}}}


def addItem(user, reminder):
    todo = Todo(todo=reminder, done=False, user=user)
    db.session.add(todo)
    db.session.commit()
    return "Added the item: " + reminder


def processMessage(sender, text):
    output = ""
    try:
        user = db.session.query(User).filter_by(userid=sender).one()
    except:
        user = User(userid = sender)
        db.session.add(user)
        db.session.commit()
        retList=["Welcome to the Todo List app on FB",
                "Thank you for visiting",
                "You can add todo items in our app",
                "Feel free to chat with our app in natural language",
                "Eg: remind me to water the plants",
                "    list all todos",
                "    mark 3 as done",
                "    show all todos",
                "    add 'something' to todo list"]
        for r in retList:
            output += r + "\n"
        output += "\n"
    intent, reminder, number = getFunctionality(text)
    if intent == "greet":
        return {'text': output + "" + greetings()}
    elif intent == "done":
        return {'text': output + "" + markDone(user, number)}
    elif intent == "list":
        x = listAll(user=user,output=output)
        pprint.pprint(x)
        return x
    elif intent == "showdone":
        return {'text': output + "" + listAll(user=user,all=False)}
    elif intent == "add":
        return {'text': output + "" + addItem(user, reminder)}
    else:
        return {'text': output + "" + "Sorry did not get you...\nTry again"}



if __name__ == '__main__':
    app.run(debug=True)
