from flask import Flask, render_template, redirect
from forms.login import RegisterForm
from forms.autorization import LoginForm
from data import db_session
from data.users import User
from data.courses import Course
from data.chapters import Chapter
from flask_login import LoginManager, login_required, login_user
from flask_login import logout_user, current_user
import json


app = Flask(__name__)
app.config['SECRET_KEY'] = 'very_very_very_unsecret_for_me'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    k = "    [\
        {   'id': '0',\
            'text': '2+2',\
            'type': 'input',\
            'answer': '4'\
        },\
        {\
            'id': '1',\
            'text': 'Выбирите планеты',\
            'type': 'checkbox',\
            'answer': [1, 1, 0],\
            'elements': [{'text': 'Юпитер', 'id': '0'}, {'text': 'Земля', 'id': '1'}, {'text': 'Солнце', 'id': '2'}]\
        },\
        {\
            'id': '2',\
            'text': '3 + 5',\
            'type': 'radio',\
            'answer': 0,\
            'elements': [{'text': '8', 'id': '0'}, {'text': '7', 'id': '1'}]\
        }\
    ]"
    k = k.replace("'", '"')
    print(k)
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        courses = db_sess.query(Course).filter(
            (Course.user == current_user) | (Course.is_private != True))
    else:
        courses = db_sess.query(Course).filter(Course.is_private != True)
    return render_template("index.html", courses=courses)


@app.route("/user/<id>")
def user(id):
    try:
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == id)[0]
        user_courses = db_sess.query(Course).filter(Course.id.in_(user.last_chapters_json))
        return render_template("user.html", user=user,
                               user_courses=user_courses)
    except Exception:
        return render_template('error.html')


@app.route("/course/<course_id>/<chapter_id>/")
def course(course_id, chapter_id):
    try:
        db_sess = db_session.create_session()
        chapter = db_sess.query(Chapter).filter(Chapter.num == chapter_id, Chapter.course_id == course_id)[0]
        html = chapter.html
        return render_template("course.html", chapter=chapter, html=html)
    except Exception:
        return render_template("error.html")


@app.route("/course/<course_id>/<chapter_id>/test/", methods=['GET', 'POST'])
def test(course_id, chapter_id):
    db_sess = db_session.create_session()
    test = json.loads(db_sess.query(Chapter).filter(Chapter.num == chapter_id, Chapter.course_id == course_id)[0].test_json)

    return render_template("test.html", test=test, course_id=course_id, chapter_id=chapter_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()