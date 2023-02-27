from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
import os
import forms
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'sqlite.db')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Log in to see this page.'

#tables

helper_table = db.Table('helper',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('program_id', db.Integer, db.ForeignKey('programs.id')))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    # image = db.Column(db.LargeBinary, nullable=True, default='img/default.jpg')
    programs = db.relationship('Program', backref='user') #user's created programs. can be many
    followed_programs = db.relationship('Program', secondary=helper_table, backref='users') #user's followed programs. can be many

class Program(db.Model):
    __tablename__ = "programs"
    id = id = db.Column(db.Integer, primary_key=True)
    date = db.Column(DateTime, default=datetime.now())
    discription = db.Column(db.String(700), nullable=False)
    tasks = db.relationship('Task', backref='program')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id')) #user = program author. can be only one

class Task(db.Model):
    __tablename__ = "tasks"
    id = id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()

#routs

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(name=form.name.data, email=form.email.data,
                    password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You can now log in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Email or password is incorrect.', 'danger')
    return render_template('login.html', form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = forms.ProgramForm()
    if form.add_task.data:
        form.tasks.append_entry()
        return render_template('create.html', form=form)

    if request.method == 'POST' and 'delete_task' in request.form:
        # Удалить задачу из формы
        task_id = int(request.form['delete_task'])
        del form.tasks.entries[task_id]

    if form.validate_on_submit():
        # Создать новый объект программы
        program = Program(discription=form.discription.data, author_id=current_user.id)
        db.session.add(program)
        db.session.commit()
        
        # Создать новые объекты задач и связать их с программой
        for task in form.tasks.data:
            task_obj = Task(task=task['task'], program_id=program.id)
            db.session.add(task_obj)
        
        # Записать изменения в базу данных
        db.session.commit()
        
        # Перенаправить пользователя на главную страницу
        flash('Program has been successfully created!', 'success')
        return redirect(url_for('account'))
    
    return render_template('create.html', form=form)

# @app.route('/entries')
# @login_required
# def entries():
#     my_entries = Entry.query.filter_by(user_id=current_user.id).all()
#     return render_template('entries.html', all_entries=my_entries, datetime=datetime)


# @app.route('/all_entries')
# @login_required
# def all_entries():
#     all_entries = Entry.query.all()
#     return render_template('all_entries.html', all_entries=all_entries, datetime=datetime)


@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = forms.UpdateAccountForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template("account.html", form=form)


# @app.route('/balance')
# @login_required
# def balance():
#     all_entries = Entry.query.filter_by(user_id=current_user.id)
#     balance = 0
#     for entry in all_entries:
#         if entry.income:
#             balance += entry.sum
#         else:
#             balance -= entry.sum
#     return render_template('balance.html', balance=balance)


# @app.route('/delete/<id>')
# @login_required
# def delete(id):
#     entry = Entry.query.get(id)
#     if entry.user_id != current_user.id:
#         return redirect(url_for('index'))
#     db.session.delete(entry)
#     db.session.commit()
#     return redirect(url_for('entries'))


# @app.route('/update/<id>', methods=['GET', 'POST'])
# @login_required
# def update(id):
#     entry = Entry.query.get(id)
#     if entry.user_id != current_user.id:
#         return redirect(url_for('index'))
#     form = forms.EntryForm()
#     if form.validate_on_submit():
#         print(form.sum.data)
#         entry.sum = form.sum.data
#         entry.income = form.income.data
#         db.session.commit()
#         flash('You have updated entry successfully', 'success')
#         return redirect(url_for('entries'))
#     elif request.method == 'GET':
#         form.sum.data = entry.sum
#         form.income.data = entry.income
#     return render_template('update.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
