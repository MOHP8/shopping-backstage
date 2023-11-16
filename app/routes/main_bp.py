from flask import Flask, render_template, request, redirect, url_for, current_app, Blueprint, session, jsonify
from werkzeug.utils import secure_filename
from database import Database
import os
from uuid import uuid4
import pandas as pd
from datetime import datetime
import base64
from app.routes.helpers import save_product_image, UPLOAD_FOLDER ,allowed_file

main_bp = Blueprint('main', __name__)
database = Database()


# UPLOAD_FOLDER = 'uploads
@main_bp.route('/', methods=['GET', 'POST'])
def home():
    select_query = f"SELECT * FROM Orders"
    orders = database.get_data(select_query)
    orders = [(item[0], item[1], item[2].strftime("%Y-%m-%d %H:%M"), item[3], item[4]) for item in orders]
    print(orders)

    select_query = f"SELECT * FROM Products WHERE Deletedate IS NULL"
    all_products = database.get_data(select_query)
    column_names = ['UUID', 'id', 'category', 'name', 'stock', 'price', 'image', 'product_date', 'update_date',
                    'update_column', 'delete_date']

    # 建一DataFrame
    df = pd.DataFrame(all_products, columns=column_names)

    # 將DataFrame轉為字典
    all_products = df.to_dict(orient='records')
    print(all_products)

    return render_template('index.html', orders=orders, all_products=all_products)


@main_bp.route('/members', methods=['POST'])
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

@main_bp.route('/products')
def all_products():

    select_query = f"SELECT * FROM Products"
    all_products = database.get_data(select_query)
    column_names = ['UUID', 'id', 'category', 'name', 'stock', 'price', 'image', 'product_date', 'update_date',
                    'update_column', 'delete_date']

    # 建一DataFrame
    df = pd.DataFrame(all_products, columns=column_names)

    # 將DataFrame轉為字典
    all_products = df.to_dict(orient='records')
    print(all_products)
    return render_template("products.html", all_products=all_products)

# ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/products', methods=['POST'])
def add_product():
    if request.method == 'POST':
        try:
            uuid = str(uuid4())
            product_name = request.form.get('productName')
            product_category = request.form.get('productCategory')
            product_stock = request.form.get('productStock')
            product_price = request.form.get('productPrice')
            product_img = request.files.get('productPic')
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            img_data = save_product_image(product_img, product_name)

            # 将图片的二进制数据保存到数据库
            insert_product_query = f"INSERT INTO Products (UUID, ProductCategory, ProductName, Stock, Price, Image, ProductDate, UpdateDate, DeleteDate) " \
                                   f"VALUES ('{uuid}', '{product_category}', '{product_name}', {product_stock}, {product_price}, " \
                                   f"%s, '{current_date}', Null, Null);"

            database.insert_data(insert_product_query, (img_data,))

            return redirect(url_for('main.home'))

        except Exception as e:
            print(e)
            return "发生错误"

@main_bp.route('/products/<product_id>')
def get_product_info(product_id):
    select_query = f"SELECT * from Products WHERE ProductID = {product_id}"
    product_info = database.get_data(select_query)
    column_names = ['UUID', 'id', 'category', 'name', 'stock', 'price', 'image', 'product_date', 'update_date',
                    'update_column', 'deleted']

    if not product_info:
        # 處理當找不到指定 id 的產品的情況
        return jsonify({'error': 'Product not found'}), 404

    # 將資料轉換為字典
    product_info_dict = dict(zip(column_names, product_info[0]))

    # 從資料庫中讀取二進制圖片數據
    image_data = product_info_dict['image']

    # 將二進制圖片數據轉換為 base64 編碼
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    # 添加 base64 編碼的圖片數據到字典中
    product_info_dict['image_base64'] = image_base64

    # 移除原始的 bytes 圖片數據，避免 JSON 序列化錯誤
    product_info_dict.pop('image')

    print("product_info", product_info_dict)
    return jsonify(product_info_dict)

@main_bp.route('/products/modify/<int:product_id>', methods=['POST'])
def save_modified_data(product_id):

    # 获取修改后的数据
    modified_data = request.form.to_dict()
    print(modified_data)
    product_name = modified_data['ProductName']
    product_img = request.files.get('productPic')
    print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZz')
    print(product_name)
    print(product_img)

    img_data = save_product_image(product_img, product_name)

    modified_columns = list(modified_data.keys())
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("modified", modified_data)

    # 模拟更新数据库中的商品信息
    if modified_data:
        try:
            conn, cursor = database.connect_mysql()

            # 更新数据库
            update_query = "UPDATE Products SET image = %s, UpdateDate = %s WHERE ProductID = %s;"
            cursor.execute(update_query, (img_data, current_date, product_id))

            conn.commit()
            return jsonify({'message': 'Data saved successfully'})
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to save data'}), 500
        finally:
            cursor.close()
            conn.close()
    else:
        return jsonify({'error': 'Product not found'}), 404

@main_bp.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    print("delete", product_id)
    if product_id:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn, cursor = database.connect_mysql()
        update_query = f"UPDATE Products SET DeleteDate = '{current_date}'  WHERE ProductID = {product_id};"
        cursor.execute(update_query)
        conn.commit()
        return jsonify({'message': 'Data saved successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404

@main_bp.route('/products/revive/<int:product_id>', methods=['POST'])
def revive_product(product_id):
    print("revive", product_id)
    if product_id:
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn, cursor = database.connect_mysql()
        update_query = f"UPDATE Products SET DeleteDate = NULL, UpdateDate = '{current_date}'  WHERE ProductID = {product_id};"
        cursor.execute(update_query)
        conn.commit()
        return jsonify({'message': 'Data saved successfully'})
    else:
        return jsonify({'error': 'Product not found'}), 404


# def edit_product(product_id):
#     select_query = f"SELECT * from Products WHERE ProductID = {product_id}"
#     product_info = database.get_data(select_query)
#     column_names = ['UUID', 'id', 'category', 'name', 'stock', 'price', 'image','product_date', 'update_date']
#     print(product_info)
#     # 建一DataFrame
#     df = pd.DataFrame(product_info, columns=column_names)
#     print(df)
#     if not product_info:
#         # 處理當找不到指定 id 的產品的情況
#         return 'product_not_found'  # 創建一個模板來處理這種情況
#
#     # 將DataFrame轉為字典
#     product_info = df.iloc[0].to_dict()
#     print(product_info)
#
#
#     # 將DataFrame轉為字典
#     product_info = df.to_dict(orient='records')
#     print("edit", product_info)
#     return jsonify(product_info)
#     # return redirect(url_for('main.home', product_info=product_info))
#

# @main_bp.route('/product', methods=['GET', 'POST'])
# def manage():
#     # select_query = f"SELECT * FROM Orders"
#     # orders = database.get_data(select_query)
#     # orders = [(item[0], item[1], item[2].strftime("%Y-%m-%d %H:%M"), item[3], item[4]) for item in orders]
#     # print(orders)
#     select_query = f"SELECT * FROM Products"
#     products = database.get_data(select_query)
#     print(products)
#     return render_template('products.html', products=products)
