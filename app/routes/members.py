from flask import Blueprint, render_template, request,redirect, url_for, jsonify
from database import Database
from datetime import datetime
from app.routes.main_bp import login_required

members = Blueprint('members', __name__)
database = Database()

@members.route('/members')
@login_required
def all_members():
    conn, cursor = database.connect_mysql()
    select_query = f"SELECT * FROM Members"
    all_members = database.get_data_to_dict(select_query)
    print(all_members)
    return render_template("members.html", all_members=all_members)

@members.route('/member/add', methods=['POST'])
def add_member():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        insert_query = (f"INSERT INTO Members (MemberName, Email, Password, RegistrationDate, ModificationDate, State)"
                        f"VALUES (%s, %s, %s, NOW(), Null , 1);")
        database.insert_data(insert_query, (username, email))
        select_query = f"SELECT * from Members"
        data = database.get_data(select_query)
        print(data)
    return redirect(url_for('members.all_members'))

@members.route('/members/delete/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    print("delete", member_id)
    try:
        if member_id:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn, cursor = database.connect_mysql()
            update_query = f"UPDATE members SET State = 2  WHERE MemberID = {member_id};"
            cursor.execute(update_query)
            conn.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@members.route('/members/<member_id>')
def get_member_info(member_id):
    select_query = f"SELECT * from members WHERE MemberID = {member_id}"
    member_info = database.get_data_to_dict(select_query)

    if not member_info:
        # 處理當找不到指定 id 的產品的情況
        return jsonify({'error': 'Member not found'}), 404

    print("member_info", member_info)
    return jsonify(member_info)

@members.route('/members/revive/<int:member_id>', methods=['POST'])
def revive_member(member_id):
    print("revive", member_id)
    if member_id:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn, cursor = database.connect_mysql()
        update_query = f"UPDATE members SET State = 1 WHERE MemberID = {member_id};"
        cursor.execute(update_query)
        conn.commit()
        print("here")
        return jsonify({'message': 'Data saved successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404