from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
import os
import forms
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from datetime import datetime
from werkzeug.utils import secure_filename

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
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('program_id', db.Integer, db.ForeignKey('programs.id'), nullable=False))

completed_programs_table = db.Table('completed_programs',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), nullable=False),
    db.Column('program_id', db.Integer, db.ForeignKey('programs.id'), nullable=False))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    image = db.Column(db.String(120), nullable=True, default='default.png')
    programs = db.relationship('Program', backref='user') #user's created programs. can be many
    followed_programs = db.relationship('Program', secondary=helper_table, backref='users') #user's followed programs. can be many
    completed_programs = db.relationship('Program', secondary=completed_programs_table, backref='users_completed')

class Program(db.Model):
    __tablename__ = "programs"
    id = id = db.Column(db.Integer, primary_key=True)
    date = db.Column(DateTime, default=datetime.now())
    description = db.Column(db.String(700), nullable=False)
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


@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = forms.PhotoForm()
    my_programs = Program.query.filter_by(author_id=current_user.id)
    completed_programs_num = len(current_user.completed_programs)
    return render_template("account.html", form=form, my_programs=my_programs, num=completed_programs_num)


@app.route('/update_photo', methods=['POST'])
@login_required
def update_photo():
    form = forms.PhotoForm()
    if form.validate_on_submit():
        if form.photo.data:
            # Удаление старого фото пользователя (если оно существует)
            if current_user.image != 'default.png':
                try:
                    os.remove(os.path.join(app.root_path, 'static/img', current_user.image))
                except:
                    pass

            # Сохранение нового фото пользователя
            f = form.photo.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.root_path, 'static/img', filename))
            current_user.image = filename
            db.session.commit()
            flash('Your profile picture has been updated!', 'success')
            return redirect(url_for('account'))

    flash('An error occurred while updating your profile picture.', 'danger')
    return redirect(url_for('account'))


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
        program = Program(description=form.description.data, author_id=current_user.id)
        db.session.add(program)
        db.session.commit()
        
        # Создать новые объекты задач и связать их с программой
        for task in form.tasks.data:
            task_obj = Task(task=task['task'], program_id=program.id)
            db.session.add(task_obj)
        
        db.session.commit()
        
        flash('Program has been successfully created!', 'success')
        return redirect(url_for('account'))
    
    return render_template('create.html', form=form)

@app.route('/delete/<id>')
@login_required
def delete(id):
    program = Program.query.get(id)
    if program.author_id != current_user.id:
        return redirect(url_for('account'))
    db.session.delete(program)
    db.session.commit()
    return redirect(url_for('account'))

@app.route('/all_programs', methods=["GET", "POST"])
def all_programs():
    all_programs = Program.query.all()
    return render_template("all_programs.html", all_programs=all_programs)

@app.route('/follow/<int:id>', methods=["GET", "POST"])
@login_required
def follow(id):
    program = Program.query.get(id)
    current_user.followed_programs.append(program)
    db.session.commit()
    flash("You are now following this program")
    return redirect(url_for('all_programs'))

@app.route('/followed_programs', methods=["GET", "POST"])
@login_required
def followed_programs():
    followed_programs = current_user.followed_programs
    form = forms.CompleteForm()
    return render_template('followed_programs.html', followed_programs=followed_programs, form=form)

@app.route('/remove/<id>')
@login_required
def remove(id):
    program = Program.query.get(id)
    if program in current_user.followed_programs:
        current_user.followed_programs.remove(program)
        db.session.commit()
    return redirect(url_for('followed_programs'))

@app.route('/complete/<id>', methods=["POST"])
@login_required
def complete(id):
    program = Program.query.get(id)
    current_user.completed_programs.append(program)
    db.session.commit()
    flash(f"Congratulations! You have completed the program: {program.description}")
    return redirect(url_for('followed_programs'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
