from flask import request, send_from_directory, render_template, jsonify, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash

from shooter import app, db
from shooter.models import *
from shooter.helper import *
from shooter.site_config import *


#################### Web Pages ####################


@app.route('/')
def search_page():
    print(current_user)
    return render_template('search.html')


@app.route('/login')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('search_page'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout_page():
    logout_user()
    return redirect(url_for('search_page'))


@app.route('/teacher/<teacher_name>')
def teacher_page(teacher_name):
    try:
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

    except Exception as e:
        return render_template('error.html', error_msg='Server error!')


@app.route('/rate/<teacher_name>')
@login_required
def rate_page(teacher_name):
    try:
        # Try fetching teacher from database
        teacher = Teacher.query.filter_by(name=teacher_name).first()

        # If teacher does not exist, return error page
        if not teacher:
            return render_template('error.html', error_msg='Teacher not found!')

        return render_template('rate.html', teacher_id=teacher.id,
                                            teacher_name=teacher.name)

    except Exception as e:
        return render_template('error.html', error_msg='Server error!')



#################### APIs ####################


@app.route('/get-teachers', methods=['POST'])
def get_teachers():
    '''
    Response JSON: (code: int, msg: str, *data: list[str], *error: str)
        code: info code
            0: successful
            1: server error (possible a bandwidth / network problem)
        msg: description of response
        *data: names of all teachers (code == 0)
        *error: description of the error (code == 1)
    '''

    try:
        return jsonify({'code': 0, 'msg': 'Success', 'data': [i.name for i in Teacher.query.all()]})
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
                return jsonify({'code': 2, 'msg': 'Server error', 'error': 'Unknown'})

            # User credentials validated, insert into database
            hashed_password = generate_password_hash(password)
            user_obj = User(school_id=username, name=name, password=hashed_password)
            db.session.add(user_obj)
            db.session.commit()

            login_user(user)
            return jsonify({'code': 0, 'msg': 'Success'})

    except Exception as e:
        return jsonify({'code': 2, 'msg': 'Server error', 'error': str(e)})


@app.route('/get-ratings', methods=['POST'])
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

    teacher_id = request.form['teacher_id']
    offset = request.form['offset']

    if not offset.isdigit():
        return jsonify({'code': 1, 'msg': 'Invalid parameters'})
    else:
        offset = int(offset)

    results = Rating.query.filter_by(teacher_id=teacher_id).offset(RATING_PAGE_SIZE * offset).limit(RATING_PAGE_SIZE).all()
    results = [[i.class_id, i.rating, i.comment, i.ups, i.downs, i.created.timestamp()] for i in results]

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

    # Get all classes that the teacher teaches
    class_ids = Teach.query.filter_by(teacher_id=teacher_id).all()
    classes = {i.class_id: Class.query.get(i.class_id).name for i in class_ids}

    classes[1] = 'N/A'

    return jsonify({'code': 0, 'msg': 'Success', 'data': classes})


@app.route('/rate', methods=['POST'])
@login_required
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
    user_id = None if not current_user else current_user.id

    # Validations
    if not user_id:
        return jsonify({'code': 1, 'msg': 'Invalid user ID, try logging in again'})

    if rating not in ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'):
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
