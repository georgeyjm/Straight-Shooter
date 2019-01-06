import requests
from bs4 import BeautifulSoup


class Database:
    '''Abstraction of a Flask-MySQL instance.'''

    def __init__(self, mysql):
        self.mysql = mysql


    def _escape(self, user_input: str) -> str:
        '''Escape an input string to avoid SQL Injection.'''
        return user_input


    def fetchone(self, query: str, *formats: str):
        '''Fetch the first result from a given SQL query.'''
        # Create SQL query
        formats = tuple(map(self._escape, formats))
        query = query.format(*formats)
        # Perform SQL query
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()
        return result


    def fetchall(self, query: str, *formats: str):
        '''Fetch the first result from a given SQL query.'''
        # Create SQL query
        formats = tuple(map(self._escape, formats))
        query = query.format(*formats)
        # Perform SQL query
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result


    def insert(self, query: str, *formats: str):
        '''Insert data into database using a given SQL query.'''
        # Create SQL query
        formats = tuple(map(self._escape, formats))
        query = query.format(*formats)
        # Perform SQL query
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        cursor.execute("SELECT LAST_INSERT_ID()")
        insert_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return insert_id


    def update(self, query: str, *formats: str):
        '''Updates one or more cells in the database using a given SQL query.'''
        # Create SQL query
        formats = tuple(map(self._escape, formats))
        query = query.format(*formats)
        # Perform SQL query
        conn = self.mysql.connect()
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return 0


def ykps_auth(username: str, password: str):
    '''
    Return: (ret: int, name: str)
        ret: info/exit code
            0: successful
            1: invalid credentials
            2: request error (possibly network (timeout) error)
        name: name of the user (if ret != 0, name will be the error)
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

