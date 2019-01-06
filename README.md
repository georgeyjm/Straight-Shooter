# Straight Shooter

Flask app of an online teacher rating platform for YK Pao School.


## Deployment

If you want to deploy this app on your own server, follow this guide.

### Database

Straight Shooter uses MySQL as its backend database management system.

1. Set up your MySQL server.

2. Create a database named `shooter` and switch to it.

```mysql
CREATE DATABASE `shooter` DEFAULT CHARSET utf8mb4;
USE `shooter`;
```

3. Create tables.

### Script

1. Clone this repository.

```shell
git clone https://github.com/yu-george/Straight-Shooter.git
```

2. Create `secrets.py` in the root directory of the cloned repository with the following format

```python
APP_SECRET_KEY = 'YOUR_APP_SECRET_KEY'

MYSQL_DB = {
    'HOST': 'YOUR_DB_HOST',
    'DB': 'YOUR_DB_NAME',
    'USER': 'YOUR_DB_USER',
    'PASSWORD': 'YOUR_DB_PASSWORD'
}
```

3. Run the flask app and enjoy.

```shell
FLASK_APP=shooter.py flask run --host 0.0.0.0
```
