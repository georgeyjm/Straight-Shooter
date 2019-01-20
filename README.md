# Straight Shooter

Flask app of an online teacher rating platform for YK Pao School.


## Deployment

If you want to deploy this app on your own server, follow this guide.

### Database

Straight Shooter uses MySQL as its backend database management system.

1. Set up your MySQL server.

2. Create a database and switch to it.

```mysql
CREATE DATABASE `YOUR_DB_NAME` DEFAULT CHARSET utf8mb4;
USE `YOUR_DB_NAME`;
```

3. Create tables.

4. Install dependencies.
```shell
pip install flask flask-sqlalchemy flask-login flask-caching requests bs4
```

### Script

1. Clone this repository.

```shell
git clone https://github.com/yu-george/Straight-Shooter.git
```

2. Create `instance/secrets.py` in the root directory of the cloned repository with the following format

```python
SECRET_KEY = 'YOUR_APP_SECRET_KEY'

_MYSQL_USERNAME = 'MYSQL_DB_USERNAME'
_MYSQL_PASSWORD = 'MYSQL_DB_PASSWORD'
_MYSQL_HOST = 'MYSQL_DB_HOSTNAME'
_MYSQL_DBNAME = 'YOUR_DB_NAME'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4'.format(_MYSQL_USERNAME, _MYSQL_PASSWORD, _MYSQL_HOST, _MYSQL_DBNAME)

```

3. Run the flask app by

```shell
FLASK_APP=shooter flask run --host 0.0.0.0
```
or alternatively
```shell
python run.py
```
