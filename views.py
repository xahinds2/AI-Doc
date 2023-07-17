from flask_login import current_user
from flask import render_template, request, jsonify
from pymongo import MongoClient
import openai

client = MongoClient('mongodb+srv://xahinds2:Sahindas1%40@expensemanager.gcbsdlg.mongodb.net/')
db = client['ExpenseApp']
collection = db['users']


def home():
    is_login = current_user.is_authenticated
    return render_template('home.html', isLogin=is_login)


def profile():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        collection.insert_one(form_data)
        msg = "Form data saved successfully"
        return render_template('profile.html', msg=msg)

    return render_template('profile.html')


def chatgpt_query(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": user_input
        }],
        temperature=0
    )
    return response.choices[0].message["content"]


def dashboard():
    if request.method == 'POST':
        age = 50
        gender = 'male'
        symptoms = request.form['symptoms']
        query = f"I am {age} {gender}, i am having {symptoms}, I know that you are not doctor but " \
                f"please provide information on the possible causes of the above symptom."
        resp = chatgpt_query(query)
        return render_template('dashboard.html', resp=resp)

    return render_template('dashboard.html')


def diet():
    if request.method == 'POST':
        age = 50
        gender = 'male'
        symptoms = request.form['symptoms']
        query = f"I am {age} {gender}, i am having {symptoms}, " \
                f"please provide information on the foods to eat and avoid for the above symptom."
        resp = chatgpt_query(query)
        return render_template('diet.html', resp=resp)

    return render_template('diet.html')


def lifestyle():
    if request.method == 'POST':
        age = 50
        gender = 'male'
        symptoms = request.form['symptoms']
        query = f"I am {age} {gender}, i am having {symptoms}, " \
                f"please provide information on the lifestyle changes that may cure the above symptom."
        resp = chatgpt_query(query)
        return render_template('lifestyle.html', resp=resp)

    return render_template('lifestyle.html')
