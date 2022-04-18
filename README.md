## Requirements
* Python 3.6
* Pip 3 (installed with Python3)

```bash
# MacOS
$ brew install python3

# Linux
sudo apt install python3
```

## Installation
To install virtualenv via pip run:
```bash
$ pip3 install virtualenv
```

## Usage
#### Creation of virtualenv:
```bash
$ virtualenv -p python3 venv

# If the above code does not work, you could also do
$ python3 -m venv venv
```

#### To activate the virtualenv:
```bash
$ source venv/bin/activate

# Windows (https://stackoverflow.com/questions/8921188/issue-with-virtualenv-cannot-activate)

$ venv\Scripts\activate
```

### Deactivate the virtualenv (after you finished working):
```
$ deactivate
```

## Run Application
Start the server by running:
```bash
# Install dependencies in virtual environment
$ pip3 install -r requirements.txt
$ pip3 install psycopg2-binary --force-reinstall --no-cache-dir
$ export FLASK_ENV=development
$ export FLASK_APP=web
$ python3 -m flask run
```

### Migrate the database
```bash
$ python3 manage.py db init
$ python3 manage.py db migrate
$ python3 manage.py db upgrade
```

Alternatively, you can run:
```
$ flask db init
$ flask db migrate
$ flask db upgrade
```
You should see such a line after running the migration command: `INFO  [alembic.autogenerate.compare] Detected added table 'user'`

## Unit Tests
To run the unit tests use the following commands:
```
$ python3 -m venv venv_unit
$ source venv_unit/bin/activate
$ pip install -r requirements-unit.txt
$ export DATABASE_URL='sqlite:///web.db'
$ pytest unit_test
```
## Integration Tests
Start by running the web server in a separate terminal.

Now run the integration tests using the following commands:
```
$ python3 -m venv venv_integration
$ source venv_integration/bin/activate
$ pip3 install -r requirements-integration.txt
$ pytest integration_test
```

