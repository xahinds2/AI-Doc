from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask import Flask, render_template, url_for, redirect, request
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'

client = MongoClient('mongodb+srv://xahinds2:Sahindas1%40@expensemanager.gcbsdlg.mongodb.net/')
db = client['ExpenseApp']
collection = db['users']
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password']


@login_manager.user_loader
def load_user(user_id):
    user_data = collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None


@app.route('/')
def home():
    return render_template('home.html', isLogin=current_user.is_authenticated)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user_data = collection.find_one({'username': username})
        if user_data:
            if bcrypt.check_password_hash(user_data['password'], password):
                login_user(User(user_data))
                return redirect(url_for('dashboard'))

        return render_template('login.html',
                               error='Username or Password is wrong!')

    return render_template('login.html')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        name = request.form['name']

        user_data = collection.find_one({'username': username})

        if user_data:
            return render_template('signup.html',
                                   error='Username already exist!')

        hashed_password = bcrypt.generate_password_hash(password)
        user_data = {
            'username': username,
            'password': hashed_password,
            'name': name,
            'email': email,
            'role': 'User'
        }
        collection.insert_one(user_data)
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('home.html')


@app.route('/delete_user/<username>')
def delete_user(username):
    collection.delete_one({'username': username})
    return redirect(url_for('users'))


@app.route('/users/')
@login_required
def users():
    user_list = collection.find()
    return render_template('users.html', user_list=user_list)


if __name__ == "__main__":
    app.run()
