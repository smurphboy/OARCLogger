# OARCLogger

OARC QSO Logger

## TL;DR

The OARC QSO Logger is a database backed web application written in Python using the Flask framework. It allows a set of users to capture, import and manage QSOs. It's initial aim is to support Worked All OARC, but it is capable of expanding into other use cases.

## Stack used

Python 3.8 / Flask 2.2 / Postgres (other SQL databases will work / Nginx (other WGSI servers can be used)

## Installation

* Install python requirements e.g. pip3 install -r requirements.txt
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

In live mode use initd??? (TBC)

## and finally...

This repository is the code for OARC QSO logging solution. This builds on work done for Worked All OARC in June and July 2022 by M0SMU - Simon.

Please feel free to take what you need from this and use it to help others to play some radio

73

M0SMU - Simon
