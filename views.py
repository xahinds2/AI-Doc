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


def dashboard():
    # from javascript the /chat function is called
    return render_template('dashboard.html')


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
