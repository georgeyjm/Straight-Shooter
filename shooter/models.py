from flask_login import UserMixin
from werkzeug.security import check_password_hash

from shooter import db, login_manager


class Class(db.Model):
    '''Model for classes table.'''

    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Class {}>'.format(self.name)


class Rating(db.Model):
    '''Model for ratings table.'''

    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    ups = db.Column(db.Integer, nullable=False, default=0)
    downs = db.Column(db.Integer, nullable=False, default=0)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return '<Rating {}>'.format(self.id)


class Teacher(db.Model):
    '''Model for teachers table.'''

    __tablename__ = 'teachers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    rating = db.Column(db.Float, nullable=False, default=0)

    def __repr__(self):
        return '<Teacher {}>'.format(self.name)


class Teach(db.Model):
    '''Model for teaches table.'''

    __tablename__ = 'teaches'

    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))

    def __repr__(self):
        return '<Teach {}>'.format(self.id)


class User(UserMixin, db.Model):
    '''Model for ratings table.'''

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(80), nullable=False, unique=True)
    name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    downs = db.Column(db.Integer, nullable=False, default=0)
    ups = db.Column(db.Integer, nullable=False, default=0)
    contribution = db.Column(db.Float, nullable=False, default=0)
    conduct = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def authenticate(self, password):
        '''Checks if provided password matches hashed password.'''
        return check_password_hash(self.password, password)


class Vote(db.Model):
    '''Model for ratings table.'''

    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rating_id = db.Column(db.Integer, db.ForeignKey('ratings.id'))
    type = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return '<Vote {}>'.format(self.id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




# class Employee(UserMixin, db.Model):
#     """
#     Create an Employee table
#     """

#     # Ensures table will be named in plural and not in singular
#     # as is the name of the model
#     __tablename__ = 'employees'

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(60), index=True, unique=True)
#     username = db.Column(db.String(60), index=True, unique=True)
#     first_name = db.Column(db.String(60), index=True)
#     last_name = db.Column(db.String(60), index=True)
#     password_hash = db.Column(db.String(128))
#     department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
#     is_admin = db.Column(db.Boolean, default=False)

#     def authenticate(self, password):
#         """
#         Check if hashed password matches actual password
#         """
#         return check_password_hash(self.password_hash, password)

#     @property
#     def password(self):
#         """
#         Prevent pasword from being accessed
#         """
#         raise AttributeError('password is not a readable attribute.')

#     @password.setter
#     def password(self, password):
#         """
#         Set password to a hashed password
#         """
#         self.password_hash = generate_password_hash(password)

#     def verify_password(self, password):
#         """
#         Check if hashed password matches actual password
#         """
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return '<Employee: {}>'.format(self.username)


# class Department(db.Model):
#     """
#     Create a Department table
#     """

#     __tablename__ = 'departments'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(60), unique=True)
#     description = db.Column(db.String(200))
#     employees = db.relationship('Employee', backref='department',
#                                 lazy='dynamic')

#     def __repr__(self):
#         return '<Department: {}>'.format(self.name)


# class Role(db.Model):
#     """
#     Create a Role table
#     """

#     __tablename__ = 'roles'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(60), unique=True)
#     description = db.Column(db.String(200))
#     employees = db.relationship('Employee', backref='role',
#                                 lazy='dynamic')

#     def __repr__(self):
#         return '<Role: {}>'.format(self.name)
