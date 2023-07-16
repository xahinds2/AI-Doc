from bson import ObjectId
from flask_bcrypt import Bcrypt
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask import Flask, render_template, url_for, redirect, request, jsonify
from pymongo import MongoClient
import openai

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'

openai.api_key = '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'

client = MongoClient('mongodb+srv://xahinds2:Sahindas1%40@expensemanager.gcbsdlg.mongodb.net/')
db = client['ExpenseApp']
collection = db['users']
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# user login and signup functionality

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data['username']
        self.password = user_data['password']


@login_manager.user_loader
def load_user(user_id):
    user_data = collection.find_one({'_id': ObjectId(user_id)})
    return User(user_data)


@app.route('/')
def home():
    is_login = current_user.is_authenticated
    return render_template('home.html', isLogin=is_login)


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

        msg = 'Username or Password is wrong!'
        return render_template('login.html', error=msg)

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
            msg = 'Username already exist!'
            return render_template('signup.html', error=msg)

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


@app.route('/delete_user/<username>')
def delete_user(username):
    collection.delete_one({'username': username})
    return redirect(url_for('users'))


@app.route('/users/')
@login_required
def users():
    user_list = collection.find()
    return render_template('users.html', user_list=user_list)


# dashboard section starts here

@app.route('/dashboard/')
def dashboard():
    # from javascript the /chat function is called
    return render_template('dashboard.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": user_input
        }],
        temperature=0
    )
    response = response.choices[0].message["content"]
    return jsonify({'response': response})


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/submit_form/', methods=['POST'])
def submit_form():
    form_data = request.form.to_dict()

    # Save data to MongoDB
    result = collection.insert_one(form_data)

    if result.acknowledged:
        return jsonify({"message": "Form data saved successfully"})
    else:
        return jsonify({"error": "Failed to save form data"}), 500


if __name__ == "__main__":
    app.run()


search_String = """
**Medical Query: Causes of Symptoms**

Symptom: [chest pain, headache, burping]
past medical conditions = []
family medical history = []
past surgeries = []
allergies = []
medications or supplements you are taking = []
Chronic diseases = []
Physical Examination Findings = []
Vital Signs = []
Sample Photos = []
Any Relevant Tests = []

Please provide information on the possible causes of the above symptom.
Include both common and rare conditions that may lead to experiencing this symptom.

1. **Common Causes**: List the most prevalent medical conditions or factors that can lead to the occurrence of this symptom.

2. **Less Common Causes**: Include less frequent but noteworthy conditions associated with this symptom.

3. **Severity**: Indicate whether this symptom could be a sign of a serious medical issue or if it is typically harmless.

4. **Additional Symptoms**: Mention any other symptoms that might accompany the primary symptom, as they could provide valuable context.

5. **Risk Factors**: Discuss any known risk factors that increase the likelihood of experiencing this symptom.

6. **When to Seek Medical Advice**: Provide guidance on when an individual should consult a healthcare professional regarding this symptom.
"""