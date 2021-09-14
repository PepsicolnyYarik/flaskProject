from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
import sqlite3
import os
from FDataBase import FDataBase
from UserLogin import UserLogin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm
from admin.admin import admin


DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78gsdgsdgsd@#5?>gfhf89dx,v06k'
USERNAME = 'admin'
PASSWORD = '123'
MAX_CONTENT_LENGTH = 1024 * 1024

app = Flask(__name__)

app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))
app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Pls log in to fuck me'
dbase = None


@app.before_request
def before_request():
    global dbase
    db = connect_db()
    dbase = FDataBase(db)


def connect_db():
    connect = sqlite3.connect(app.config['DATABASE'])
    connect.row_factory = sqlite3.Row
    return connect


def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)


@app.route('/', methods=['POST', 'GET'])
def main_page():
    if request.method == 'POST' and request.form == 'city_name' and len(request.form['city_name']) > 0:
        flash('Success', category='success')
    return render_template('index.html', menu=dbase.getMenu())


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/add_post', methods=["POST", 'GET'])
@login_required
def add_post():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
    return render_template('add_post.html', menu=dbase.getMenu())


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        if len(request.form['email']) > 5:
            flash('Сообщение отправлено')
        else:
            flash('Ошибка отправки')
    return render_template('contact.html', menu=dbase.getMenu())


@app.route('/profile', methods=["POST", "GET"])
@login_required
def profile():
    return render_template('profile.html', menu=dbase.getMenu())


@app.route('/user_avatar', methods=['POST', 'GET'])
@login_required
def user_avatar():
    img = current_user.getAvatar(app)
    if not img:
        return ''
    h = make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h


@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")

    return redirect(url_for('profile'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = dbase.getUserByEmail(form.email.data)
        if user and check_password_hash(user['psw'], form.psw.data):
            user_login = UserLogin().create(user)
            rm = form.remember.data
            login_user(user_login,remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))
        else:
            flash('Неверная пара логин/пароль', 'error')

    return render_template('login.html', menu=dbase.getMenu(), form=form)
    # if request.method == 'POST':
    #     user = dbase.getUserByEmail(request.form['email'])
    #     if user and check_password_hash(user['psw'], request.form['psw']):
    #         user_login = UserLogin().create(user)
    #         rm = True if request.form.get('remainme') else False
    #         login_user(user_login,remember=rm)
    #         return redirect(request.args.get('next') or url_for('profile'))
    #     else:
    #         flash('Неверная пара логин/пароль', 'error')
    # return render_template('base_admin.html', menu=dbase.getMenu())


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        gen_hash = generate_password_hash(form.psw.data)
        res = dbase.addUser(form.name.data, form.email.data, gen_hash)
        if res:
            flash('Вы успешно зарегистрированы', 'success')
            return redirect(url_for('login'))
        else:
            flash('Ошибка регистрации', 'error')
    # if request.method == 'POST':
    #     if len(request.form['name']) > 5 and len(request.form['email']) > 5 and len(request.form['psw']) > 5 \
    #             and request.form['psw'] == request.form['psw2']:
    #         gen_hash = generate_password_hash(request.form['psw'])
    #         res = dbase.addUser(request.form['name'], request.form['email'], gen_hash)
    #         if res:
    #             flash('Вы успешно зарегистрированы', 'success')
    #             return redirect(url_for('login'))
    #         else:
    #             flash('Ошибка регистрации', 'error')
    #     else:
    #         flash('Неверно заполнены поля', 'error')
    return render_template('register.html', menu=dbase.getMenu(), form=form)


@app.route("/post/<alias>")
@login_required
def show_post(alias):
    title, post = dbase.getPost(alias)
    if not title:
        abort(404)
    return render_template('post.html', title=title, post=post)


@app.errorhandler(404)
def error(error):
    print(error)
    return render_template('page404.html'), 404


if __name__ == '__main__':
    app.run()
