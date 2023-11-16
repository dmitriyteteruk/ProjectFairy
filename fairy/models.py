import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from fairy import db, bcrypt, login_manager, app


@login_manager.user_loader
def load_user(santa_id):
    user = Santa.query.get(int(santa_id))
    return Santa.query.get(int(user.id))


class Santa(db.Model, UserMixin):
    __tablename__ = 'santa'

    id = db.Column(db.Integer(), primary_key=True)
    email_address = db.Column(db.String(length=60), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    first_name = db.Column(db.String(length=30), nullable=False)
    last_name = db.Column(db.String(length=30), nullable=False)
    phone = db.Column(db.String(length=15), nullable=False)
    gifts = db.relationship('Gift', backref='santa', lazy=True)
    role = db.Column(db.String(length=30), nullable=False)
    registered_on = db.Column(db.DateTime(), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=True, default=False)
    confirmed_on = db.Column(db.DateTime(), nullable=True)

    def get_reset_token(self, expires_sec=3600):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Santa.query.get(user_id)

    def __repr__(self):
        return f"User('{self.id}', '{self.email_address}', '{self.first_name}', '{self.last_name}', '{self.phone}')"

    # def __repr__(self):
    #     return '<Santa %r>' % self.last_name

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


# класс Проект
class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    delivery_date = db.Column(db.DateTime, nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False)
    gift = db.relationship('Gift', backref='project', lazy=True)
    delivery_address = db.Column(db.String(length=1000), nullable=True)
    contact_person = db.Column(db.String(length=60), nullable=True)
    phone = db.Column(db.String(length=20), nullable=True)
    pickup_point_address_1 = db.Column(db.String(length=1000), nullable=True)
    pickup_point_address_2 = db.Column(db.String(length=1000), nullable=True)


# класс Подарок
class Gift(db.Model):
    __tablename__ = 'gift'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=100), nullable=False, unique=True)
    description = db.Column(db.String(length=300), nullable=True)
    postcard_url = db.Column(db.String(length=300),  nullable=False)
    kid_id = db.Column(db.Integer, db.ForeignKey('kid.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    santa_id = db.Column(db.Integer, db.ForeignKey('santa.id'), nullable=True)
    status = db.Column(db.Integer(), nullable=True)
    status_updated_time = db.Column(db.DateTime(), nullable=True)
    status_updated_by_user = db.Column(db.Integer(), nullable=True)


    def __repr__(self):
        return f'Gift {self.name}'

    # метод назначения дарителя на подарок.
    def assign_ownership(self, user):
        self.santa_id = user.id                             # фиксируем в базе юзера за конкретными шариком
        self.status = 0                                     # меняем статус на 0
        self.status_updated_time = datetime.datetime.now()  # записываем дату и время изменений
        self.status_updated_by_user = user.id               # записываем id пользователя, который внес изменения
        db.session.commit()  # записываем данные в базу

    # метод обновления статуса подарка
    def status_update(self, status, user):
        self.status = status                                # меняем цифру
        self.status_updated_time = datetime.datetime.now()  # записываем дату и время изменений
        self.status_updated_by_user = user.id               # записываем id пользователя, который внес изменения
        db.session.commit()                                 # записываем данные в базу


# класс Ребенок
class Kid(db.Model):
    __tablename__ = 'kid'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=40), nullable=False)
    birthday = db.Column(db.DateTime, nullable=False)
    gifts = db.relationship('Gift', backref='kid', lazy=True)
    house_id = db.Column(db.Integer, db.ForeignKey('house.id'), nullable=False)

    def __repr__(self):
        return f'Kid {self.name}'


# класс Подшефное Учреждение
class House(db.Model):
    __tablename__ = 'house'

    id = db.Column(db.Integer(), primary_key=True)
    short_name = db.Column(db.String(length=50), nullable=False)
    full_name = db.Column(db.String(length=200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    email = db.Column(db.String(60), nullable=False)
    contact_person = db.Column(db.String(length=250), nullable=False)
    houses = db.relationship('Kid', backref='house', lazy=True)

    def __repr__(self):
        return f'House {self.short_name}'
