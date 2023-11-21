from flask import Blueprint, render_template, request
from database import Database
import pandas as pd

members = Blueprint('members', __name__)
database = Database()


@members.route('/members', methods=['POST'])
def add_member():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        state = request.form.get('situation')
        delete_query = f"DELETE FROM Members WHERE Email = '{email}'; "
        insert_query = f"INSERT INTO Members (MemberName, Email, Password, RegistrationDate, ModificationDate, State) VALUES ('{username}', '{email}', 'hashed_password', '2023-01-15 14:30:00', '2023-10-15 09:45:00', '{state}');"
        database.insert_data(insert_query)
        select_query = f"SELECT * from Members"
        data = database.get_data(select_query)
        print(data)
    return render_template('index.html')