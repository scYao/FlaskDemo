from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
import config
from models import User
from exts import db

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app=app)


# db.create_all()

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        telephone = request.form.get('telephone')
        password = request.form.get('password')
        user = User.query.filter(User.telephone == telephone, User.password == password).first()
        if user:
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
@app.route('/logout',methods=['GET','POST'])
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user': user}
    else:
        #必须要返回字典，即使为空
        return {}


@app.route('/question',methods=['GET','POST'])
def question():
    if request.method == 'GET':
        return render_template('question.html')
    else:
        pass


if __name__ == '__main__':
    app.run()
