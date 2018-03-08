from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import g
import config
from models import User
from models import Question
from models import Answer
from exts import db
from decorators import login_required
from sqlalchemy import or_

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app=app)


# db.create_all()

@app.route('/')
def index():
    context = {
        'questions': Question.query.order_by('-create_time').all()
    }
    return render_template('index.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            # 如果31天可以登录
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return 'telephone is wrong or password is wrong'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        telephone = request.form.get('telephone')
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # 验证手机号码是否被注册
        user = User.query.filter(User.telephone == telephone).first()

        if user:
            return 'the phone number is registered,please change phone number'
        else:
            # 确认两次输入密码是否相等
            if password != password_confirm:
                return 'the pasword input in twices is not same'
            else:
                user = User(telephone=telephone, username=username, password=password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))


# 注销
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


@app.route('/question', methods=['GET', 'POST'])
@login_required
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title, content=content)
        # user_id = session.get('user_id')
        # user = User.query.filter(User.id == user_id).first()
        question.author = g.user
        db.session.add(question)
        db.session.commit()

        return redirect(url_for('index'))


@app.route('/detail/<question_id>', methods=['GET', 'POST'])
def detail(question_id):
    if request.method == 'GET':
        question = Question.query.filter(Question.id == question_id).first()

        return render_template('detail.html', question=question)


@app.route('/add_answer', methods=['POST'])
@login_required
def add_answer():
    content = request.form.get('answer_content')
    answer = Answer(content=content)

    # user_id = session.get('user_id')
    # user = User.query.filter(User.id == user_id).first()
    answer.author = g.user

    question_id = request.form.get('question_id')
    question = Question.query.filter(Question.id == question_id).first()
    answer.question = question
    db.session.add(answer)
    db.session.commit()

    return redirect(url_for('detail', question_id=question_id))


@app.route('/search', methods=['get'])
def search():
    q = request.args.get('q')
    questions = Question.query.filter(or_(Question.title.contains(q), Question.content.contains(q))).order_by(
        '-create_time')
    return render_template('index.html', questions=questions)


@app.before_request
def my_before_request():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            g.user = user


@app.context_processor
def my_context_processor():
    if hasattr(g, 'user'):
        return {'user': g.user}
    else:
        # 必须要返回字典，即使为空
        return {}


if __name__ == '__main__':
    app.run()
