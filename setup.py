import base64
from datetime import timedelta
import uuid
from flask import Flask, Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from flask_mongoengine import MongoEngine
from flask_login import LoginManager, UserMixin, login_manager, login_required, login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['SECRET_KEY'] = "$2a$16$BV1lQz.1A11Qy3/rY3Ei4.vB4.chNJtN6xHg4Vij115UhFtFIW6mq"

app.config['REMEMBER_COOKIE_DURATION'] = timedelta(minutes=5)

app.config['REMEMBER_COOKIE_SECURE'] = True

app.config['PAYSTACK_SECRET_KEY'] = 'sk_test_25456f29977a44c76fadefd9f6d4b689cd8c801f'

app.config['PAYSTACK_PUBLIC_KEY'] = 'pk_test_dfc6cbe08454451775055477b377fe8def4f93c3'

app.config['MAIL_SERVER']='smtp.gmail.com'

app.config['MAIL_PORT'] = 465

app.config['MAIL_USERNAME'] = 'kingsonseang@gmail.com'

app.config['MAIL_PASSWORD'] = 'osIG12@$'

app.config['MAIL_USE_TLS'] = False

app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


# app.config["MONGO_URI"] = "mongodb://localhost:27017/todo_db"
# mongodb_client = PyMongo(app)
# db = mongodb_client.db

# client = pymongo.MongoClient("mongodb+srv://kingsonseang:solomonpass@test.5qltm.mongodb.net/test?retryWrites=true&w=majority")
# db = client.test

app.config['MONG_DBNAME'] = 'test'

app.config['MONGO_URI'] = 'mongodb+srv://kingsonseang:solomonpass@test.5qltm.mongodb.net/test?retryWrites=true&w=majority'

db = MongoEngine()
db.init_app(app)


class User(db.Document, UserMixin):
    meta = {'collection': 'users'}
    name = db.StringField()
    phone = db.StringField()
    email = db.EmailField()
    password = db.StringField()

    # def __init__(self, name, phone, email, password):
        # self.name = name
        # self.phone = phone
        # self.email = email
        # self.password = password

    def __init__(self, name, phone, email, password, *form, **kwform):
        super(User, self).__init__(*form, **kwform)
        self.name = name
        self.phone = phone
        self.email = email
        self.password = password


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email


class Booking(db.Document):
    meta = {'collection': 'booking'}
    name = db.StringField()
    email = db.EmailField()
    Adult = db.StringField()
    Child = db.StringField()
    suite = db.StringField()
    check_in = db.StringField()
    check_out = db.StringField()
    status = db.StringField()
    payment_ref = db.StringField()
    special_request = db.StringField()

    def __init__(self, name, email, Adult, Child, suite, special_request, check_in, check_out, status, payment_ref, *form, **kwform):
        super(Booking, self).__init__( *form, **kwform)
        self.name = name
        self.email = email
        self.Adult = Adult
        self.Child = Child
        self.suite = suite
        self.check_in = check_in
        self.check_out = check_out
        self.status = status
        self.payment_ref = payment_ref
        self.special_request = special_request



login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
app.permanent_session_lifetime = timedelta(weeks=5)  

@login_manager.user_loader
def load_user(email):
    return User.objects(email=email).first()


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/services/')
def services():
    return render_template('service.html')


@app.route('/contact/', methods=['GET', 'POST'])
def contact():
    if request.method == "GET":
        return render_template('contact.html')
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        msg = Message(message, sender=email, recipients=['kingsonseang@gmail.com'], body=subject)
        mail.send(msg)
        return redirect(url_for('contact'))
    


@app.route('/rooms/')
def rooms():
    return render_template('room.html')


@app.route('/booking/', methods=['GET', 'POST'])
def booking():
    if request.method == "GET":
        id = uuid.uuid1()
        id = int(id)
        return render_template('booking.html', id=id)
    if request.method == "POST":
        name = request.form.get('name')
        status = request.form.get('status')
        email = request.form.get('email')
        check_in = request.form.get('checkin')
        check_out = request.form.get('checkout')
        Adult = request.form.get('Adult')
        Child = request.form.get('Child')
        suite = request.form.get('suite')
        message = request.form.get('message')
        payment_ref = request.form.get('ref')

        new_booking = Booking(name=name, email=email, check_in=check_in, check_out=check_out, Adult=Adult, Child=Child, suite=suite, special_request=message, status=status, payment_ref=payment_ref)
        new_booking.save()

        if new_booking.status == 'sucess':
            return redirect(url_for('booking'))

        return redirect(url_for('booking'))




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('root'))


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == "GET":
        return render_template('signin.html')
    if request.method == "POST":
        # name = request.form.get('name')
        # name = re.split(r'\s+', name)
        _fname = request.form.get('fname')
        _lname = request.form.get('lname')
        _name = _fname + " " + _lname
        _email = request.form.get('email')
        _tel = request.form.get('tel')
        _pwrd = request.form.get('pwrd')
        _pwrd2 = request.form.get('pwrd2')
        
        user = User.objects(email=_email).first()
        print(user)

        if user:
            flash('Email already exists.', category='error')
            return redirect(url_for('sign_up'))
        elif len(_fname or _lname) < 2:
            flash('each name must be more than 3 characters.', category='error')
            return redirect(url_for('sign_up'))
        elif _pwrd != _pwrd2:
            flash('password don\'t match.', category='error')
            return redirect(url_for('sign_up'))
        elif len(_pwrd) < 7:
            flash('password must be more than 7 characters.', category='error')
            return redirect(url_for('auth.sign_up'))
        else:
            print(_fname, _lname, _email, _tel, _pwrd)
            user = User(name=_name, email=_email, phone=_tel, password=generate_password_hash(_pwrd, method='sha256'))
            user.save()
            return redirect(url_for('login'))

    return redirect(url_for('auth.login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pwrd')
        print(password)

        user = User.objects(email=email).first()

        if user:
            print(password)
            if check_password_hash(user['password'], password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('root'))
            else:
                flash('Incorrect password, try again.', category='error')
                return redirect(url_for('login'))
        else:
            flash('Email does not exist.', category='error')
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/test')
def pay():
    return render_template('pay.html')


# @app.route("/send")
# def index():
#    msg = Message('Hello Again', sender = 'info@solomon.com', recipients = ['ogevie1136@gmail.com'])
#    msg.body = "Hello Flask message sent from Flask-Mail"
#    mail.send(msg)
#    return "Sent"


if __name__ == '__main__':
    app.run(debug=True, port=8080)
