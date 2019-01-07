import os
import sys
import time
from functools import wraps

from flask import Flask, request, send_from_directory, render_template, jsonify, redirect, url_for, session
from flaskext.mysql import MySQL
# from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash

from helper import *
from secrets import *


os.chdir(os.path.dirname(os.path.abspath(__name__)))


#################### App Initialization ####################

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

mysql = MySQL()
app.config['MYSQL_DATABASE_HOST'] = MYSQL_DB['HOST']
app.config['MYSQL_DATABASE_DB'] = MYSQL_DB['DB']
app.config['MYSQL_DATABASE_USER'] = MYSQL_DB['USER']
app.config['MYSQL_DATABASE_PASSWORD'] = MYSQL_DB['PASSWORD']
mysql.init_app(app)
db = Database(mysql)

# login_manager = LoginManager()
# login_manager.init_app(app)



#################### Constants Declaration ####################


CONDUCT_CURRENT_VERSION = 1

PAGE_NUM = 10
NUM_RATING_SIGNIFICANT = 3
MAX_COMMENT_LENGTH = 25565



#################### Cache Initialization ####################


teacher_ratings = {}

# Due to the static-ness of this data, it will be stored as a constant
ALL_TEACHERS = [i[0] for i in db.fetchall("SELECT `teacher_name` FROM `teachers`")]



#################### Core Functions ####################


def update_session(logged_in=None, user_id=None, name=None, conduct=None):
    if logged_in != None:
        session['logged_in'] = logged_in
    if user_id != None:
        session['user_id'] = user_id
    if name != None:
        session['name'] = name
    if conduct != None:
        session['conduct'] = conduct
    return 0


def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in', False):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return wrapper


def update_teacher_overall(teacher_id, new_rating, user_id):
    '''Updates the overall score of a teacher before a new rating is inserted.
    Currently only using simple arithmetic mean, will change in future.'''

    current_overall = db.fetchone("SELECT `rating` FROM `teachers` WHERE `teacher_id` = '{}'", teacher_id)
    num_ratings = db.fetchone("SELECT count(*) FROM `ratings` WHERE `teacher_id` = '{}'", teacher_id)

    current_overall = current_overall[0]
    num_ratings = num_ratings[0]
    new_rating = int(new_rating) / 2

    new_overall = (num_ratings * current_overall + new_rating) / (num_ratings + 1)

    db.update("UPDATE `teachers` SET `rating` = '{}' WHERE `teacher_id` = '{}'", new_overall, teacher_id)
    return 0



#################### Web Pages ####################


@app.route('/')
def search_page():
    return render_template('search.html')


@app.route('/login')
def login_page():
    if session.get('logged_in', False):
        return redirect(url_for('search_page'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout_page():
    update_session(logged_in=False)
    return redirect(url_for('search_page'))


@app.route('/teacher/<teacher_name>')
def teacher_page(teacher_name):
    try:
        # Try fetching teacher from database
        teacher = db.fetchone("SELECT * FROM `teachers` WHERE `teacher_name` = '{}'", teacher_name)

        # If teacher does not exist, return error page
        if not teacher:
            return render_template()

        # Check if the user has already rated this teacher
        have_rated = False
        if session.get('logged_in', False):
            user_id = session.get('user_id')
            teacher_id = teacher[0]
            if db.fetchone("SELECT `rating_id` FROM `ratings` WHERE `user_id` = '{}' AND `teacher_id` = '{}'", user_id, teacher_id):
                have_rated = True

        num_ratings = db.fetchone("SELECT count(*) FROM `ratings` WHERE `teacher_id` = '{}'", teacher_id)[0]
        if num_ratings < NUM_RATING_SIGNIFICANT:
            teacher_overall = 'N/A'
        else:
            teacher_overall = round(teacher[2], 1)

        return render_template('teacher.html', teacher_id=teacher[0],
                                               teacher_name=teacher[1],
                                               teacher_overall=teacher_overall,
                                               have_rated=have_rated)

    except Exception as e:
        return jsonify({'code': 2, 'msg': 'Server error', 'error': str(e)})


@app.route('/rate/<teacher_name>')
@require_login
def rate_page(teacher_name):
    try:
        # Try fetching teacher from database
        teacher = db.fetchone("SELECT * FROM `teachers` WHERE `teacher_name` = '{}'", teacher_name)

        # If teacher does not exist, return error page
        if not teacher:
            return render_template()

        return render_template('rate.html', teacher_id=teacher[0],
                                            teacher_name=teacher[1])

    except Exception as e:
        return jsonify({'code': 2, 'msg': 'Server error', 'error': str(e)})



#################### APIs ####################


@app.route('/get-teachers', methods=['POST'])
def get_teachers():
    try:
        return jsonify({'code': 0, 'msg': 'Success', 'data': ALL_TEACHERS})
    except Exception as e:
        return jsonify({'code': 1, 'msg': 'Server error', 'error': str(e)})


@app.route('/login', methods=['POST'])
def authenticate():
    '''
    Response JSON: (code: int, description: str, name: str)
        code: info code
            0: successful
            1: invalid credentials
            2: server error (possible a bandwidth / network problem)
        msg: description of response
        *error: description of the error (code == 2)
    '''

    try:
        username = request.form['username']
        password = request.form['password']
    except:
        return jsonify({'code': 1, 'msg': 'Missing user credentials'})
    
    try:
        # Try fetching user from database
        user = db.fetchone("SELECT * FROM `users` WHERE `school_id` = '{}'", username)

        # If user is already in the database, validate credentials
        if user:
            if check_password_hash(user[3], password):
                # Password is correct, update session
                update_session(logged_in=True, user_id=user[0], name=user[2], conduct=user[7])
                return jsonify({'code': 0, 'msg': 'Success'})
            else:
                return jsonify({'code': 1, 'msg': 'Invalid user credentials'})

        # New user trying to log in
        else:
            # Authenticate via PowerSchool
            ret, name = ykps_auth(username, password)
            if ret == 1:
                return jsonify({'code': 1, 'msg': 'Invalid user credentials'})
            elif ret == 2:
                return jsonify({'code': 2, 'msg': 'Server error', 'error': 'Unknown'})

            # User credentials validated, insert into database
            hashed_password = generate_password_hash(password)
            user_id = db.insert("INSERT INTO `users` (`school_id`, `name`, `password`) VALUES ('{}', '{}', '{}')", username, name, hashed_password)

            update_session(logged_in=True, user_id=user_id, name=name, conduct=0)
            return jsonify({'code': 0, 'msg': 'Success'})

    except Exception as e:
        return jsonify({'code': 2, 'msg': 'Server error', 'error': str(e)})


@app.route('/get-ratings', methods=['POST'])
def get_ratings():
    '''
    Response JSON: (code: int, description: str, name: str)
        code: info code
            0: successful
            1: invalid parameters
        msg: description of response
        data: ratings data of the structure
            [
                [
                    class_id,
                    rating,
                    comment,
                    ups,
                    downs,
                    created_ts
                ],
                ...
            ]
    '''

    teacher_id = request.form['teacher_id']
    offset = request.form['offset']

    if not offset.isdigit():
        return jsonify({'code': 1, 'msg': 'Invalid parameters'})
    else:
        offset = int(offset)

    results = db.fetchall("SELECT `class_id`, `rating`, `comment`, `ups`, `downs`, UNIX_TIMESTAMP(`created`) FROM `ratings` WHERE `teacher_id` = '{}' LIMIT {}, {}", teacher_id, PAGE_NUM * offset, PAGE_NUM)

    return jsonify({'code': 0, 'msg': 'Success', 'data': results})


@app.route('/get-classes', methods=['POST'])
def get_classes():
    '''
    Response JSON: (code: int, description: str, name: str)
        code: info code
            0: successful
        msg: description of response
        data: classes data of the structure
            {
                'class_id_1': 'class_name_1',
                'class_id_2': 'class_name_2',
                ...
            }
    '''

    teacher_id = request.form['teacher_id']

    class_ids = db.fetchall("SELECT `class_id` FROM `teaches` WHERE `teacher_id` = '{}'", teacher_id)
    class_ids = map(lambda x: str(x[0]), class_ids)
    class_ids = ','.join(class_ids)
    if not class_ids:
        results = ()
    else:
        results = db.fetchall("SELECT `class_id`, `class_name` FROM `classes` WHERE class_id IN ({})", class_ids)

    classes = {i: j for i, j in results}
    classes[1] = 'N/A'

    return jsonify({'code': 0, 'msg': 'Success', 'data': classes})


@app.route('/rate', methods=['POST'])
@require_login
def rate_teacher():
    '''
    Response JSON: (code: int, description: str, name: str)
        code: info code
            0: successful
            1: invalid user ID
            2: invalid rating value
            3: invalid comment length
            4: teacher not found
            5: class not found
            6: invalid class (class is not taught by the given teacher)
        msg: description of response
    '''

    teacher_id = request.form['teacher_id']
    class_id = request.form['class_id']
    rating = request.form['rating']
    comment = request.form['comment']
    user_id = session.get('user_id', None)

    # Validations
    if not user_id:
        return jsonify({'code': 1, 'msg': 'Invalid user ID, try logging in again'})

    if rating not in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'):
        return jsonify({'code': 2, 'msg': 'Invalid rating value'})

    if len(comment) == 0 or len(comment) > MAX_COMMENT_LENGTH:
        return jsonify({'code': 3, 'msg': 'Invalid comment length'})

    if not db.fetchone("SELECT * FROM `teachers` WHERE `teacher_id` = '{}'", teacher_id):
        return jsonify({'code': 4, 'msg': 'Teacher not found'})

    if not db.fetchone("SELECT * FROM `classes` WHERE `class_id` = '{}'", class_id):
        return jsonify({'code': 5, 'msg': 'Class not found'})

    if class_id != '1' and not db.fetchone("SELECT * FROM `teaches` WHERE `teacher_id` = '{}' AND `class_id` = '{}'", teacher_id, class_id):
        return jsonify({'code': 6, 'msg': 'Invalid class'})

    # Update the teacher's overall rating
    update_teacher_overall(teacher_id, rating, user_id)

    # Data validated, perform insertion
    db.insert("INSERT INTO `ratings` (`user_id`, `teacher_id`, `class_id`, `rating`, `comment`) VALUES ('{}', '{}', '{}', '{}', '{}')", user_id, teacher_id, class_id, rating, comment)
    return jsonify({'code': 0, 'msg': 'Success'})

