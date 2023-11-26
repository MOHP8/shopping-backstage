from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from database import Database
from datetime import datetime
from werkzeug.security import generate_password_hash ,check_password_hash
from app.routes.main_bp import login_required

staffs = Blueprint('staffs', __name__)
database = Database()


@staffs.route('/staffs')
@login_required
def all_staffs():
    select_query = f"SELECT * FROM Staffs"
    all_staffs = database.get_data_to_dict(select_query)
    print(all_staffs)
    return render_template("staffs.html", all_staffs=all_staffs)


@staffs.route('/staffs', methods=['POST'])
def add_staff():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 檢查密碼是否匹配
        if password != confirm_password:
            flash('密碼和確認密碼不一致', 'error')

            # 儲存原始數據以便重新填充表單
            session['original_data'] = {
                'username': username,
                'email': email,
            }
            return redirect(url_for('staffs.all_staffs'))
        session.pop('original_data', None)
        password = generate_password_hash(password)

        insert_query = (f"INSERT INTO Staffs  (StaffName, Email, Password, RegistrationDate, ModificationDate, State) VALUES ( %s, %s, %s, NOW(), NULL, 1);")
        database.insert_data(insert_query, (username, email, password))
        select_query = f"SELECT * from Staffs"

    return redirect(url_for('staffs.all_staffs'))


@staffs.route('/staffs/delete/<int:staff_id>', methods=['POST'])
def delete_staff(staff_id):
    print("delete", staff_id)
    try:
        if staff_id:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn, cursor = database.connect_mysql()
            update_query = f"UPDATE Staffs SET State = 2  WHERE StaffID = {staff_id};"
            cursor.execute(update_query)
            conn.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Staff not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@staffs.route('/staffs/<staff_id>')
def get_staff_info(staff_id):
    select_query = f"SELECT * from staffs WHERE staffID = {staff_id}"
    staff_info = database.get_data_to_dict(select_query)

    if not staff_info:
        # 處理當找不到指定 id 的產品的情況
        return jsonify({'error': 'Member not found'}), 404

    print("member_info",staff_info)
    return jsonify(staff_info)


@staffs.route('/staffs/revive/<int:staff_id>', methods=['POST'])
def revive_staff(staff_id):
    print("revive", staff_id)
    if staff_id:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn, cursor = database.connect_mysql()
        update_query = f"UPDATE Staffs SET State = 1 WHERE StaffID = {staff_id};"
        cursor.execute(update_query)
        conn.commit()
        print("here")
        return jsonify({'message': 'Data saved successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404
