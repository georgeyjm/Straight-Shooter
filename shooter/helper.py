import requests
from bs4 import BeautifulSoup

from shooter import app, db
from shooter.models import Teacher, Rating


def ykps_auth(username: str, password: str):
    '''
    Authenticates the given credentials through Powerschool.

    Return: (ret: int, name: str)
        ret: info/exit code
            0: successful
            1: invalid credentials
            2: request error (possibly network (timeout) error)
        name: name of the user (if ret != 0, will be the error)
    '''
    
    url = 'https://powerschool.ykpaoschool.cn/guardian/home.html'
    form_data = {
        'account': username,
        'ldappassword': password,
        'pw': 'shooter'
    }

    try:
        req = requests.post(url, data=form_data, timeout=5)
        soup = BeautifulSoup(req.text, 'html.parser')
        name = soup.select('#userName > span')[0].get_text().strip()
        ret = 0
    except Exception as e:
        name = str(e)
        ret = 1

    return ret, name


def update_teacher_overall(teacher_id: int, new_rating: int, user_id: int):
    '''Updates the overall score of a teacher before a new rating is inserted.
    Currently only using simple arithmetic mean, will change in future.'''

    teacher = Teacher.query.get(teacher_id)
    current_overall = teacher.rating
    num_ratings = Rating.query.filter_by(teacher_id=teacher_id).count()

    new_rating = int(new_rating) / 2

    new_overall = (num_ratings * current_overall + new_rating) / (num_ratings + 1)

    teacher.rating = new_overall
    db.session.commit()
    return 0
