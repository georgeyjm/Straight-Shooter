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


#################### Cache Initialization ####################

CONDUCT_CURRENT_VERSION = 1

PAGE_NUM = 10

teacher_ratings = {}

# Due to the static-ness of this data, it will be stored as a constant
ALL_TEACHERS = [i[0] for i in db.fetchall("SELECT `teacher_name` FROM `teachers`")]


def update_session(logged_in=None, user_id=None, name=None, conduct=None):
    session['logged_in'] = logged_in or session['logged_in']
    session['user_id'] = user_id or session['user_id']
    session['name'] = name or session['name']
    session['conduct'] = conduct or session['conduct']
    return 0


def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in', False):
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return wrapper


# @login_manager.user_loader
# def load_user(user_id):
#   try:
#       db_conn = mysql.connect()
#       cursor = db_conn.cursor()
#       db_conn.close()
#   except Exception as e:
#       return False 


# @app.route('/get-ratings/<teacher_name>', methods=['POST'])
# # @app.route('/get-ratings/<teacher_name>/')
# def get_ratings(teacher_name):
#     try:
#         db_conn = mysql.connect()
#         cursor = db_conn.cursor()
#         cursor.execute('SELECT * FROM `teachers` WHERE `teacher_name` = \'{}\''.format(teacher_name))
#         data = cursor.fetchone()
#         teacher_id = data[0]
#         cursor.execute('SELECT * FROM `ratings` WHERE `teacher_id` = \'{}\''.format(teacher_id))
#         data = cursor.fetchall()
#         data = [[ j for j in i] for i in data]
#         tot = sum([i[4] for i in data]) / len(data) / 2
#         teacher_ratings[teacher_name] = tot
#         db_conn.close()
#         return jsonify({'msg': 'success', 'data': data, 'rating': tot})
#     except Exception as e:
#         return jsonify({'msg': 'error', 'error': str(e)})


# @app.route('/class/<class_id>', methods=['POST'])
# def get_class(class_id):
#     try:
#         db_conn = mysql.connect()
#         cursor = db_conn.cursor()
#         cursor.execute('SELECT * FROM `classes` WHERE `class_id` = \'{}\''.format(class_id))
#         data = cursor.fetchone()
#         class_name = data[2]
#         db_conn.close()
#         return class_name
#     except Exception as e:
#         return jsonify({'msg': 'error', 'error': str(e)})


# @app.route('/teacher/<teacher_name>')
# def teacher_page(teacher_name):
#     if teacher_name in ('teacher.css', 'teacher.js'):
#         return send_from_directory('static/teacher', teacher_name)
#     else:
#         session['last_visited'] = '/teacher/' + teacher_name

#     try:
#         # db_conn = mysql.connect()
#         # cursor = db_conn.cursor()
#         # cursor.execute('SELECT * FROM `teachers` WHERE `teacher_name` = \'{}\''.format(teacher_name))
#         # data = cursor.fetchone()

#         # Try fetching teacher from database
#         teacher = db.fetchone("SELECT * FROM `teachers` WHERE `teacher_name` = '{}'", teacher_name)

#         # If teacher does not exist, return error page
#         if not teacher:
#             return render_template()

#         # This also works, depends
#         if not teacher_name in ALL_TEACHERS:
#             pass

#         if session.get('logged_in'):
#             return render_template('teacher.html', teacher_name=teacher_name, overall_rating=teacher_rating, up_votes=1000, down_votes=10, username = session['username'])
#         else:
#             return render_template('teacher.html', teacher_name=teacher_name, overall_rating=teacher_rating, up_votes=1000, down_votes=10)

#     except Exception as e:
#         return jsonify({'msg': 'error', 'error': str(e)})



# @app.route('/teacher1/<teacher_name>')
# @app.route('/teacher1/<teacher_name>/')
# def teacher1_page(teacher_name):
#     try:
#         db_conn = mysql.connect()
#         cursor = db_conn.cursor()
#         cursor.execute('SELECT * FROM `teachers` WHERE `teacher_name` = \'{}\''.format(teacher_name))
#         data = cursor.fetchone()
#         teacher_name = data[1]
#         teacher_rating = data[2]
#         teacher_id = data[0]
#         cursor.execute('SELECT * FROM `ratings` WHERE `teacher_id` = \'{}\''.format(teacher_id))
#         data = cursor.fetchall()
#         data = [[j for j in i] for i in data]
#         tot = ''
#         if len(data) == 0:
#             tot = 'Not rated'
#         else:
#             tot = '{}'.format(round(sum([i[4] for i in data]) / len(data) / 2, 1))
#             teacher_ratings[teacher_name] = tot
#         db_conn.close()
#         return render_template(
#             'teacher1.html',
#             teacher_name=teacher_name,
#             overall_rating=tot,
#             up_votes=1000,
#             down_votes=10,
#             ratings=data,
#             )
#     except Exception as e:
#         return jsonify({'msg': 'error', 'error': str(e)})


# @app.route('/confirm-tos', methods=['POST'])
# def confirm():
#     if session.get('logged_in'):
#         session['agreed'] = 1
#         return jsonify({'success': 1})
#     else:
#         return jsonify({'success': 0})


# @app.route('/rate/<teacher_name>', methods=['POST', 'GET'])
# def rate(teacher_name):
#     if request.method == 'GET':
#         if teacher_name in ('rate.css', 'rate.js'):
#             return send_from_directory('static/rate', teacher_name)
#         if not session.get('logged_in'):
#             return redirect(url_for('login'))
#         session['last_visited'] = "/rate/" + teacher_name
#         return render_template('rate.html', teacher_name=teacher_name)
#     else:
#         rating = request.form['rating']
#         comment = request.form['comment']
#         try:
#             # Check if user is logged in 
#             if session.get('logged_in'):
#                 db_conn = mysql.connect()
#                 cursor = db_conn.cursor()
#                 # Get user_id from student id
#                 cursor.execute('SELECT * FROM `users` WHERE `school_id` = \'{}\''.format(session.get('student_id')))
#                 data = cursor.fetchone()
#                 user_id = data[0]
#                 db_conn.close()
#                 # Get class_id
#                 class_id = 1
#                 # Get teacher_id
#                 db_conn = mysql.connect()
#                 cursor = db_conn.cursor()
#                 cursor.execute("SELECT * FROM `teachers` WHERE `teacher_name` = '{}'".format(teacher_name))
#                 data = cursor.fetchone()
#                 teacher_id = data[0]
#                 cursor.execute("INSERT INTO `ratings` (`user_id`, `teacher_id`, `class_id`, `rating`, `comment`) VALUES ('{}', '{}', '{}', '{}', '{}')".format(user_id, teacher_id, class_id, rating, comment))
#                 db_conn.commit()
#                 db_conn.close()
#                 return jsonify({'success': 1, 'link': '/teacher/{}'.format(teacher_name)})
#             else:
#                 return jsonify({'success': 2})
#         except Exception as e:
#             _, __, exc_tb = sys.exc_info()
#             return jsonify({'success': 0, "error": '{} at {}'.format(str(e), exc_tb.tb_lineno)})


#################### Web Pages ####################


@app.route('/')
def search_page():
    return render_template('search.html')


@app.route('/login')
def login_page():
    # if session.get('logged_in'):
    #     return redirect(url_for('send_index'))
    # else:
    return render_template('login.html')


@app.route('/login/')
def login_page_alt():
    return redirect(url_for('login_page'))


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

        teacher_overall = teacher[2] or 'N/A'
        return render_template('teacher.html', teacher_id=teacher[0],
                                               teacher_name=teacher[1],
                                               teacher_overall=teacher_overall)

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

    if len(comment) == 0 or len(comment) > 25565:
        return jsonify({'code': 3, 'msg': 'Invalid comment length'})

    if not db.fetchone("SELECT * FROM `teachers` WHERE `teacher_id` = '{}'", teacher_id):
        return jsonify({'code': 4, 'msg': 'Teacher not found'})

    if not db.fetchone("SELECT * FROM `classes` WHERE `class_id` = '{}'", class_id):
        return jsonify({'code': 5, 'msg': 'Class not found'})

    if class_id != '1' and not db.fetchone("SELECT * FROM `teaches` WHERE `teacher_id` = '{}' AND `class_id` = '{}'", teacher_id, class_id):
        return jsonify({'code': 6, 'msg': 'Invalid class'})

    # Data validated, perform insertion
    db.insert("INSERT INTO `ratings` (`user_id`, `teacher_id`, `class_id`, `rating`, `comment`) VALUES ('{}', '{}', '{}', '{}', '{}')", user_id, teacher_id, class_id, rating, comment)
    return jsonify({'code': 0, 'msg': 'Success'})

