from flask import Blueprint, render_template, request
from database import Database
import pandas as pd

main_bp = Blueprint('main', __name__)
database = Database()

@main_bp.route('/', methods=['GET', 'POST'])
def home():
    select_query = f"SELECT * FROM Orders"
    orders = database.get_data(select_query)
    orders = [(item[0], item[1], item[2].strftime("%Y-%m-%d %H:%M"), item[3], item[4]) for item in orders]
    print(orders)

    select_query = f"SELECT * FROM Products WHERE state = 1"
    all_products = database.get_data(select_query)
    column_names = ['UUID', 'id', 'category', 'name', 'stock', 'price', 'image', 'product_date', 'update_date',
                    'state']

    # 建一DataFrame
    df = pd.DataFrame(all_products, columns=column_names)

    # 將DataFrame轉為字典
    all_products = df.to_dict(orient='records')
    print(all_products)
    # return render_template('index.html', orders=orders, all_products=all_products)
    return render_template('index_new.html', orders=orders, all_products=all_products)

@main_bp.route('/left_menu', methods=['GET', 'POST'])
def left_menu():
    return render_template('left_menu.html')
