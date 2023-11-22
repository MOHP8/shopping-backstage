from flask import Flask, render_template, request, redirect, url_for, current_app, Blueprint, session, jsonify
from werkzeug.utils import secure_filename
from database import Database
import os
from uuid import uuid4
import pandas as pd
from datetime import datetime


orders = Blueprint('orders', __name__)
database = Database()

@orders.route('/orders')
def all_orders():
    conn, cursor = database.connect_mysql()
    select_query = f"SELECT * FROM Orders"
    cursor.execute(select_query)
    columns = [column[0] for column in cursor.description]
    # 將結果轉換為字典形式
    all_orders = [dict(zip(columns, row)) for row in cursor.fetchall()]

    print(all_orders)
    return render_template("orders.html", all_orders=all_orders)

@orders.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    print("delete", order_id)
    try:
        if order_id:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn, cursor = database.connect_mysql()
            update_query = f"UPDATE Orders SET State = 2  WHERE OrderID = {order_id};"
            cursor.execute(update_query)
            conn.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

