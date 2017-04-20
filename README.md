# RiverScope

A website to display river levels and level trends across all gauging stations in the UK, and provide customisable alerts on river levels. It will be useful for anyone using rivers for business or recreation, such as kayakers looking for high, fast water, pleasure boat owners who may need to adjust mooring lines, anglers looking for slow water and people with flood concerns.

## Requirements

This application is built using Django and Python 3

## Installation
### Set up the database
```bash
# Designed for Ubuntu, install the required dependency packages
$ sudo apt-get update
$ sudo apt-get install libpq-dev postgresql postgresql-contrib postgis*
# Set up the database owner for RiverScope
$ sudo su - postgres
$ psql
postgres=# CREATE USER riverscopeowner WITH PASSWORD 'password';
postgres=# ALTER ROLE riverscopeowner SET client_encoding TO 'utf8';
postgres=# ALTER ROLE riverscopeowner SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE riverscopeowner SET timezone TO 'UTC';
postgres=# CREATE DATABASE riverscope OWNER riverscopeowner;
postgres=# \connect riverscope;
postgres=# CREATE EXTENSION postgis;
postgres=# \q;
# Check that we can login to the db with new user
$ psql -U riverscopeowner -h localhost -d riverscope
riverscope=> \q
```

### Clone repo, install dependencies and setup
```bash
# Clone the repo
$ git clone https://github.com/jamesnunn/riverscope.git
# Change into the cloned repo
$ cd riverscope
# Create a virtual environment (note we use python3)
$ virtualenv venv_riverscope -p python3
# Activate the virtual environment
$ source venv_riverscope/bin/activate
# Install production dependencies
$ pip install -r requirements.txt
# Install development dependencies
$ pip install -r requirements_dev.txt
# Apply migrations to db
$ python manage.py makemigrations
$ python manage.py migrate
# Set up a superuser and start the server
$ python manage.py createsuperuser
$ python manage.py runserver
# Run tests
$ pytest test
```

## Management
### Update the database with stations published by the EA

```bash
$ python manage.py getstations
# Optionally use `-r` to get the stage typical level range but this takes minutes to run
$ python manage.py getstations -r
```
