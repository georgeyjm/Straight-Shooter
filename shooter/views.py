from functools import wraps

from flask import request, send_from_directory, render_template, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from shooter import app, db, login_manager
from shooter.models import *
from shooter.helper import *
from shooter.site_config import *


#################### Misc ####################


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_redirect():
    return redirect(url_for('login_page'))


def return_error_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _, __, exc_tb = sys.exc_info()
            return jsonify({'code': -1, 'msg': 'Server error', 'error': '{}: {}'.format(e.__class__.__name__, e), 'line': exc_tb.tb_lineno})
    return wrapper


def return_error_html(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            _, __, exc_tb = sys.exc_info()
            return render_template('error.html', error_msg='({}) {}: {}'.format(exc_tb.tb_lineno, e.__class__.__name__, e))
    return wrapper


#################### Web Pages ####################


@app.route('/')
@return_error_html
def search_page():
    return render_template('search.html')


@app.route('/login')
@return_error_html
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('search_page'))
    else:
        return render_template('login.html')


@app.route('/logout')
@return_error_html
def logout_page():
    logout_user()
    return redirect(url_for('search_page'))


@app.route('/teacher/<teacher_name>')
@return_error_html
def teacher_page(teacher_name):
    # Try fetching teacher from database
    teacher = Teacher.query.filter_by(name=teacher_name).first()

    # If teacher does not exist, return error page
    if not teacher:
        return render_template('error.html', error_msg='Teacher not found!')

    # Check if the user has already rated this teacher
    have_rated = False
    if current_user.is_authenticated:
        if Rating.query.filter_by(user_id=current_user.id, teacher_id=teacher.id).first():
            have_rated = True

    # Check if the teacher received enough ratings
    num_ratings = Rating.query.filter_by(teacher_id=teacher.id).count()
    if num_ratings < NUM_RATING_SIGNIFICANT:
        teacher_overall = 'N/A'
    else:
        teacher_overall = round(teacher.rating, 1)

    return render_template('teacher.html', teacher_id=teacher.id,
                                           teacher_name=teacher.name,
                                           teacher_overall=teacher_overall,
                                           have_rated=have_rated)


@app.route('/rate/<teacher_name>')
@login_required
@return_error_html
def rate_page(teacher_name):
    # Try fetching teacher from database
    teacher = Teacher.query.filter_by(name=teacher_name).first()

    # If teacher does not exist, return error page
    if not teacher:
        return render_template('error.html', error_msg='Teacher not found!')

    return render_template('rate.html', teacher_id=teacher.id,
                                        teacher_name=teacher.name)



#################### APIs ####################


@app.route('/get-teachers', methods=['POST'])
@return_error_json
def get_teachers():
    '''
    Response JSON: (code: int, msg: str, data: list[str])
        code: info code
            0: Success
        msg: description of response
        data: names of all teachers
    '''

    return jsonify({'code': 0, 'msg': 'Success', 'data': [i.name for i in Teacher.query.all()]})


@app.route('/login', methods=['POST'])
@return_error_json
def authenticate():
    '''
    Response JSON: (code: int, msg: str)
        code: info code
            0: Success
            1: Invalid credentials
            2: Server network error
        msg: description of response
    '''

    username = request.form.get('username')
    password = request.form.get('password')

    if not all((username, password)):
        return jsonify({'code': 1, 'msg': 'Missing user credentials'})

    # Try fetching user from database
    user = User.query.filter_by(school_id=username).first()

    # If user is already in the database, validate credentials
    if user:
        if user.authenticate(password):
            # Password is correct, login user
            login_user(user)
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
            return jsonify({'code': 2, 'msg': 'Server network error', 'error': 'Unknown'})

        # User credentials validated, insert into database
        hashed_password = generate_password_hash(password)
        user_obj = User(school_id=username, name=name, password=hashed_password)
        db.session.add(user_obj)
        db.session.commit()

        login_user(user)
        return jsonify({'code': 0, 'msg': 'Success'})


@app.route('/get-ratings', methods=['POST'])
@return_error_json
def get_ratings():
    '''
    Response JSON: (code: int, msg: str, data: list[list])
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

    teacher_id = request.form.get('teacher_id')
    offset = request.form.get('offset')

    if not offset.isdigit():
        return jsonify({'code': 1, 'msg': 'Invalid parameters'})
    else:
        offset = int(offset)

    results = Rating.query.filter_by(teacher_id=teacher_id).offset(RATING_PAGE_SIZE * offset).limit(RATING_PAGE_SIZE).all()
    results = [[i.class_id, i.rating, i.comment, i.ups, i.downs, i.created.timestamp()] for i in results]

    return jsonify({'code': 0, 'msg': 'Success', 'data': results})


@app.route('/get-classes', methods=['POST'])
@return_error_json
def get_classes():
    '''
    Response JSON: (code: int, msg: str)
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

    # Get all classes that the teacher teaches
    class_ids = Teach.query.filter_by(teacher_id=teacher_id).all()
    classes = {i.class_id: Class.query.get(i.class_id).name for i in class_ids}

    classes[1] = 'N/A'

    return jsonify({'code': 0, 'msg': 'Success', 'data': classes})


@app.route('/rate', methods=['POST'])
@login_required
@return_error_json
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

    teacher_id = request.form.get('teacher_id')
    class_id = request.form.get('class_id')
    rating = request.form.get('rating')
    comment = request.form.get('comment')
    user_id = current_user.id

    # Validations
    if not all ((teacher_id, class_id, rating, comment, user_id)):
        return jsonify({'code': 1, 'msg': 'Missing parameters'})

    if not rating.is_digit() or int(rating) not in range(1, 11):
        return jsonify({'code': 2, 'msg': 'Invalid rating value'})

    if len(comment) == 0 or len(comment) > MAX_COMMENT_LENGTH:
        return jsonify({'code': 3, 'msg': 'Invalid comment length'})

    if not Teacher.query.get(teacher_id):
        return jsonify({'code': 4, 'msg': 'Teacher not found'})

    if not Class.query.get(class_id):
        return jsonify({'code': 5, 'msg': 'Class not found'})

    if class_id != '1' and not Teach.query.filter_by(teacher_id=teacher_id, class_id=class_id).first():
        return jsonify({'code': 6, 'msg': 'Invalid class'})

    # Update the teacher's overall rating
    update_teacher_overall(teacher_id, rating, user_id)

    # Data validated, perform insertion
    rating_obj = Rating(user_id=user_id, teacher_id=teacher_id, class_id=class_id, rating=rating, comment=comment)
    db.session.add(rating_obj)
    db.session.commit()
    return jsonify({'code': 0, 'msg': 'Success'})
