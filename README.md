# Mensch Labs Coding Challenge

Welcome to the Mensch Labs Coding Challenge Setup Guide! At the end of this
guide you will have deployed a real-world Facebook Messenger Bot that you can
start talking to and experimenting with. You'll also be ready to complete the
Mensch Labs Coding Challenge!

While the choice of languages and frameworks that you use for the challenge is
up to you, we decided to make it easier to get started by providing a skeleton
app that demonstrates how to build a simple Python web app that responds to
incoming requests and interfaces with Facebook's Messenger API. This skeleton
repository contains some example code, which demonstrates the following:

* How to render HTML pages using the [Flask](http://flask.pocoo.org/) framework.
* How to create database models, populate them with data, and query them using
[SQLAlchemy](http://www.sqlalchemy.org/) and
[Flask's SQLAlchemy extension](http://flask-sqlalchemy.pocoo.org/).
* How to handle incoming webhook requests from
  [Facebook's Messenger Platform](https://developers.facebook.com/docs/messenger-platform)
  and send messages back.
* The repository also contains the relevant configuration files to make it easy
to deploy the app to Heroku. You are free to use any other hosting platform for
your bot, but it will need to be publicly accessible on the internet for it to
work, and Heroku is an easy platform to get started on.

We will use this repository as a starting point for the actual coding
challenge. Even if you decide to use a different set of frameworks, it might
still make sense to go through the initial setup steps outlined below to
understand how to connect to Facebook Messenger and how to expose your
development server to the internet for testing during development.

## Initial Setup

- Sign up for an account with [Heroku](https://heroku.com) if you don't already
have one, and log into the account. Also consider installing the
[Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) and log into the
same account (If you intend to use a different hosting platform, feel free to
skip all Heroku-specific steps and follow the instructions for deploying to your
platform instead).

- Click this button to deploy this repo as an app to Heroku:
  [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy).
  Pick an app name (e.g., `YOURNAME-ml-cc` or something similar), and remember
  it for later. Wait for the build and deployment process to finish (this will
  take a few minutes).

- Once the app is up and running, go to its root URL
  [https://YOUR-APP-NAME.herokuapp.com](https://YOUR-APP-NAME.herokuapp.com) to
  test that it works as expected. You should see a list of users and addresses.

- Likewise, navigate to `/fb_webhook` on the same app. You should see a blank
  page.

- Log into Facebook (or create an account if you don't have one), register as a
  developer (if you aren't already) and create a new app. You can use
  [this page](https://developers.facebook.com/docs/apps/register) to guide you
  through the steps.

- Create a new app. Choose suitable values for app name and contact email.

- On the left sidebar click 'Settings'. Choose "Apps for Messenger" from the category
  dropdown. Click 'Save Changes' on the bottom right.

- Click 'Add Product' on the left sidebar. Navigate to 'Messenger' and click 'Get Started'.

- On the next page, generate an access token for a Facebook Page that you want
  to use for sending and receiving messages. It's probably best to use a
  dedicated test page for this purpose. If you don't already have one, you can
  use the ["Create a page"](https://www.facebook.com/pages/create/) link on the
  page to create one. Note: You must be an admin for the page in order to
  approve the necessary permissions. Once you've generated the access token,
  make note of it, we'll need it later.

- On the same page, click "Setup Webhooks" and fill out the fields as follows:
  - Callback URL: "https://YOUR-APP-NAME.herokuapp.com/fb_webhook" (without the
    quotes).
  - Verify Token: "mysecretverifytoken" (without the quotes). This is currently
  hardcoded in the actual app code, so needs to be entered exactly like
  this. THIS IS DIFFERENT FROM THE PAGE ACCESS TOKEN GENERATED ABOVE. DO NOT
  PASTE THE PAGE ACCESS TOKEN HERE.
  - Subscription Fields: Select everything here. To start with, we only need
    "messages", but you never know what else you might want to do with this
    later... ;)

- Next, you need to subscribe to a page to receive
  updates via the webhook you just set up. In the same dialog, select the same
  page you used above and hit "Subscribe".

- Go to the [Heroku dashboard](https://dashboard.heroku.com), find your app and
  navigate to "Settings". Next, click "Reveal Config Vars" and change the value
  of the `FACEBOOK_PAGE_ACCESS_TOKEN` config variable to the access token you
  obtained above (If you have the Heroku CLI installed, you can also accomplish
  this step by running `heroku config:set
  FACEBOOK_PAGE_ACCESS_TOKEN="YOUR-ACCESS-TOKEN" -a YOUR-APP-NAME`).

- From your Facebook account, send a message to the page that you connected to
  the app above (One convenient UI for this is
  https://www.messenger.com/t/YOUR-PAGE). If all goes well the app should echo
  the message back to you (the first response may take a few seconds while
  Heroku is starting up the app)!


- Inspect the logs by going to your app in the Heroku Dashboard and click "More"
-> "View Logs". You should see log lines similar to this:

```
2017-01-25T00:29:51.540036+00:00 heroku[router]: at=info method=POST
path="/fb_webhook" host=YOUR-APP-NAME.herokuapp.com
request_id=14d930ba-b0ed-46b9-b1a9-7e0368a80e31 fwd="173.252.123.139" dyno=web.1
connect=1ms service=2ms status=200 bytes=159
```

Congrats, you've deployed a simple FB Messenger Bot!

## Local development

Note: Local development is best done on a Unix-like system, e.g. Linux or
macOS. If you're using Windows, you might be able to get this to work, but we
won't be able to offer much assistance.

To set up your local development environment to make changes to the app, go
ahead and install the following software:

- Python 2.7 (If you'd rather use Python 3, feel free to try it, but you'll
  likely have to make changes to the code in order to get it to run, so it's
  probably not recommended unless you know what you're doing.)
- git
- postgresql: A database backend we'll use.
- ngrok: A handy tool to expose your local development server to the outside
  world.

If you're on a Mac, we recommend installing all of these via [Homebrew](http://brew.sh/):

```
$ brew install python git postgresql
$ brew cask install ngrok  # To get the latest version, which is not open source
```

On Linux, most of these should be installable via your package manager of
choice (apt-get, yum, etc).

On Windows, your best bet is likely to use the
dedicated installers for each, using the following links:

- [Python](https://www.python.org/downloads/)  
- [Git](https://git-scm.com/download/win)
- [Postgresql](https://www.postgresql.org/download/windows/)

**Note:** _Make sure to add these paths to System Variables, and enter a simple password while installing Postgres_

**In windows always make sure that the Command Prompt or Powershell is running as Administrator.**

Last, install the virtualenv tool, which is needed to isolate your python
development environment from your system installation:

```
pip install virtualenv
```

(If this command fails, make sure that pip was installed when you installed
Python)

### Postgres setup

Postgres sometimes needs a bit more massaging to work properly.

After installing it, make sure it is running as a daemon in the background:

#### Mac and Linux:
```
ps auxwww | grep postgres
```

If you see a line with `/some/path/bin/postgres` in it, you're good to
go. Otherwise, start the server using `pg_ctl -D /usr/local/var/postgres -l
logfile start`. If you installed via homebrew or a package manager on Linux, you
might want to follow their corresponding instructions instead (With Homebrew,
you can typically start the server via launchctl using
[these instructions](http://stackoverflow.com/a/23628638/4946850)).

Once the server is up and running, make sure there is a database corresponding
to the local user by running

```
createdb `whoami`
```

(If this fails because this database already exists, you can ignore the error)

Next, create a database that we're going to use for this app. Run

```
createdb YOUR-APP-NAME
```

(replacing `YOUR-APP-NAME` with your actual app name, of course).

#### Windows:

Add `some\path\PostgreSQL\<version>\bin` and `some\path\PostgreSQL\<version>\lib` to the System Environment Variables.

Now to start the server, open pgAdmin 4 and navigate to: `Servers > PostgreSQL 9.* > Databases > postgres` to start the server on port 5432.

You can also start the server by running the command,

```
pg_ctl -U postgres -D "some\path\PostgreSQL\<version>\data" start
```

Now create the Database using the command:
```
createdb -U YOUR-APP-NAME
```

If all else fails, you can always fall back to using SQLite for local
development, although we still need to install Postgres-related libraries in
later stages, since that's what we're using on Heroku.

### Code setup

- Clone this repo into a directory of your choice and `cd` into it.

- Create a new virtual environment in the src directory and activate it:

#### Mac/Linux
```
virtualenv src/venv && source src/venv/bin/activate
```
#### Windows
```
virtualenv .\src\venv
.\src\venv\Scripts\activate
```

Your prompt should change to include the prefix "(venv)".

- Install the required packages into the virtual environment:
```
pip install -r requirements.txt
```

If this fails when installing psycopg2 on a Mac running El Capitan or Sierra,
[this answer](http://stackoverflow.com/a/39800677/4946850) might be helpful. If
you're running into any other issues at this step that you are unable to
resolve, please let us know.

- Set local environment variables for your database and the Facebook Page Access Token in Mac/Linux:
```
$ export FACEBOOK_PAGE_ACCESS_TOKEN="YOUR-ACCESS-TOKEN"
$ export DATABASE_URL="postgres://localhost/YOUR-APP-NAME"
```

- For Windows:
```
set FACEBOOK_PAGE_ACCESS_TOKEN=YOUR-ACCESS-TOKEN
set DATABASE_URL=postgres://<username>:<password>@localhost:5432/YOUR-APP-NAME
```
  **username is postgres and password is entered by you during setup**

- Run a script to create some DB sample data:
```
python src/db_setup.py
```

This should print out something along those lines:
```
[<app.User object at 0x1060ee890>, <app.User object at 0x1061ffe10>]
[<app.Address object at 0x10625f050>, <app.Address object at 0x10625f350>]
```

- Run the server:
```
python src/app.py
```

- Go to [http://localhost:5000](http://localhost:5000) to see the app running in
action!

### Connecting the local app to your Facebook App

- In order to receive Facebook's webhook requests during development, you need to
  expose your local server to the Internet. One easy way to do this is to use
  ngrok. In a separate terminal, start ngrok by running
```
ngrok http 5000
```

This will launch the ngrok tunneling tool, which will expose your local server
(running on port 5000) on a domain like `abcdef1235.ngrok.io`. Make sure that
this worked by going to the domain provided and checking that you still see the
same start page (make sure your server is still running in another terminal).

Note that ngrok has a handy dashboard running at
[http://localhost:4040](http://localhost:4040) where you can inspect incoming
requests and replay them as needed. This is very useful for debugging.

- Next, while your server is running, change the webhook URL for your Facebook
  app to point at `https://yoursubdomain.ngrok.io/fb_webhook` instead of the
  Heroku app. This should result in a GET request to your server from Facebook,
  to verify that your app is ready to receive responses.

- Send another message to your Facebook page and verify that this results in a
  POST request to your local server. Go to the ngrok dashboard to inspect the
  payload. Make sure that sending a message back in return worked as expected.


### Making changes and deploying to Heroku

- In your local git repo, add a Git remote for your Heroku app:

```
# Make sure you have the Heroku CLI installed and are logged in.
heroku git:remote -a YOUR-APP-NAME
```

- Make a small change to the code and commit it:
```
# Make some changes to src/app.py using your favorite editor
git add -A && git commit -m "Add some cool changes"
```


- Check that you can push to the repo as expected:
```
git push heroku master
```

This will push your current master branch to the remote `heroku`, which will
trigger the application build process on Heroku's end. Once the command
completes, your updated code should be running. You can use `heroku logs --tail`
to see updated server logs, which will include anything you print to stdout.

Now you should be all set up and ready for the coding challenge coming your way soon!
