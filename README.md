# OARCLogger

OARC QSO Logger V1 - WAOARC Season 2 edition

## TL;DR

The OARC QSO Logger is a database backed web application written in Python using the Flask framework. It allows a set of users to capture, import and manage QSOs. It's initial aim is to support Worked All OARC, but it is capable of expanding into other use cases.
This release is the Logger as at the end of WAOARC Season 2. It's a fully capable logger with ADIF import / export (although ADIF isn't checked too hard on the way in) and many visulisations.

## Stack used

Python 3.8 / Flask 2.2 / Postgres (other SQL databases will work / Nginx (other WGSI servers can be used)

## Installation

* Install python requirements e.g. pip3 install -r requirements.txt (I'd recommend a virtual env or a tool like Poetry to manage your python dependencies)
* Install database and web server

```sql
CREATE USER logger WITH PASSWORD 'logger';
ALTER ROLE logger SET client_encoding TO 'utf8';
ALTER ROLE logger SET default_transaction_isolation TO 'read committed';
ALTER ROLE logger SET timezone TO 'UTC';
CREATE DATABASE logger;
GRANT ALL PRIVILEGES ON DATABASE logger to logger;
GRANT ALL ON SCHEMA public TO logger;
```

```shell
git clone https://github.com/smurphboy/OARCLogger
```

* edit config.py with database connection details if not logger:logger

```shell
export FLASK_APP=logger.application
flask db init
flask db migrate
flask shell
```

```python
>>> from logger.application import db
>>> db.create_all()
```

## Running the server

In dev mode use:

```shell
export FLASK_APP=logger.application
flask run
```

## Setting a user as admin

Once you have the server up and you've created an initial user, you will want to make yourself ADMIN. You do this by setting the admin flag on your user record (use a POSTGRES tool to do this). 
This allows you access to the ADMIN interface at /admin so you can edit records without needing to go into the DB itself.

## Deploying the server in production setting

As above, the Flask dev server shouldn't be used on the internet! Instead there are many guides on hosting Flask applications on hosting services.
For WAOARC Season 2, I hosted it on Azure as a virtual machine based on Ubuntu 20.04, nginx and uWSGI. 
I followed this [guide](https://hackersandslackers.com/deploy-flask-uwsgi-nginx/)

## and finally...

This repository is the code for OARC QSO logging solution. This builds on work done for Worked All OARC in June and July 2022 by M0SMU - Simon.

Please feel free to take what you need from this and use it to help others to play some radio

73

M0SMU - Simon
