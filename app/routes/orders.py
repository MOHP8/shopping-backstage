from flask import Flask, render_template, request, redirect, url_for, current_app, Blueprint, session, jsonify
from werkzeug.utils import secure_filename
from database import Database
import os
from uuid import uuid4
import pandas as pd
from datetime import datetime
from app.routes.main_bp import login_required


orders = Blueprint('orders', __name__)
database = Database()

@orders.route('/orders')
@login_required
def all_orders():
    conn, cursor = database.connect_mysql()
    select_query = f"SELECT * FROM Orders"
    all_orders = database.get_data_to_dict(select_query)
    print(all_orders)

    return render_template("orders.html", all_orders=all_orders)

@orders.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    print("delete", order_id)
    try:
        if order_id:
            # current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn, cursor = database.connect_mysql()
            update_query = f"UPDATE Orders SET State = 2  WHERE OrderID = {order_id};"
            cursor.execute(update_query)
            conn.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@orders.route('/orders/<order_id>')
def get_order_info(order_id):
    select_query = f"SELECT * from Orders WHERE OrderID = {order_id}"
    order_info = database.get_data_to_dict(select_query)

    if not order_info:
        # 處理當找不到指定 id 的產品的情況
        return jsonify({'error': 'Product not found'}), 404

    print("order_info", order_info)
    return jsonify(order_info)

# @orders.route('/orders/modify/<int:order_id>', methods=['POST'])
# def save_modified_data(order_id):
#     # 获取修改后的数据
#     modified_data = request.form.to_dict()
#     print(modified_data)
#
#     current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     update_columns = [key for key in modified_data.keys()]
#
#     print("modified", modified_data)
#     print(update_columns)
#
#     # 模拟更新数据库中的商品信息
#     if modified_data:
#         try:
#             conn, cursor = database.connect_mysql()
#             set_clause = ", ".join([f"{key} = %s" for key in update_columns])
#             values = (list(modified_data.values()))
#             values.extend([order_id])
#             # values.extend([current_date, order_id])
#             print("values", values)
#             # 更新数据库
#             update_query = f"UPDATE Orders SET {set_clause} WHERE OrderID = %s;"
#             cursor.execute(update_query, values)
#             conn.commit()
#             return jsonify({'message': 'Data saved successfully'})
#         except Exception as e:
#             print(e)
#             return jsonify({'error': 'Failed to save data'}), 500
#         finally:
#             cursor.close()
#             conn.close()
#     else:
#         return jsonify({'error': 'Product not found'}), 404

@orders.route('/orders/revive/<int:order_id>', methods=['POST'])
def revive_order(order_id):
    print("revive", order_id)
    if order_id:
        # current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn, cursor = database.connect_mysql()
        update_query = f"UPDATE Orders SET State = 1 WHERE OrderID = {order_id};"
        cursor.execute(update_query)
        conn.commit()
        print("here")
        return jsonify({'message': 'Data saved successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404