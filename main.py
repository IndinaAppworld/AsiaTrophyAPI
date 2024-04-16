# This is a sample Python script.
import warnings

from flask_caching import Cache
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from datetime import datetime
import json

import calendar

# from flask_caching import Cache/\

app = Flask(__name__)
# Disable caching for database queries
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['CACHE_TYPE'] = 'null'
cache = Cache(app)

# cache = Cache(app)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'asiatrophy'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()
disable_query_cache_query = "SET GLOBAL query_cache_type = OFF;"
cursor.execute(disable_query_cache_query)

warnings.filterwarnings('ignore')


def customPrint(str):
    print(str)


def encrypt(str):
    return str;


def decrypt(str):
    return str;


# @app.route('/api/productlist', methods=['GET'])
# def productlist():
#     data = request.form['data']
#     data=decrypt(data)
#     customPrint(data)
#     data = json.loads(data)
#     ID = data.get('id')
#     TYPE=data.get('type')
#
#     STATUS = True
#     MESSAGE = "Transaction Success"


@app.route('/api/dashboard', methods=['GET'])
async def dashboard():
    # data = request.form['data']
    # data=decrypt(data)
    # customPrint(data)
    # data = json.loads(data)
    # MOBILENO = data.get('MOBILENO')

    banner_list = []
    material_list = []
    category_list = []
    STATUS = True
    MESSAGE = "Transaction Success"
    cursor = mysql.get_db().cursor()

    query = "select id,image from asiatrophybackend_banner";
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) > 0:
        for query_data in data:
            banner_response = {}
            banner_response['ID'] = str(query_data[0])
            banner_response['IMAGE'] = query_data[1]
            banner_list.append(banner_response)

    query = "select m.id,m.name,m.image,count(p.id) from asiatrophybackend_material m,asiatrophybackend_product p where m.status=1 and p.status=1 and m.id=p.material_id group by p.material_id";
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) > 0:
        for query_data in data:
            material_response = {}
            material_response['ID'] = str(query_data[0])
            material_response['NAME'] = query_data[1]
            material_response['IMAGE'] = query_data[2]
            material_response['PRODUCTCOUNT'] = query_data[3]

            material_list.append(material_response)

    query = "select id,name,image from asiatrophybackend_categories where status=1 and dashboard=1";
    cursor.execute(query)
    data = cursor.fetchall()
    if len(data) > 0:
        for query_data in data:
            category_response = {}
            category_response['ID'] = str(query_data[0])
            category_response['NAME'] = query_data[1]
            category_response['IMAGE'] = query_data[2]
            query = "select p.id,p.name,p.image,p.videolink from asiatrophybackend_product_categories pc, asiatrophybackend_product p where pc.categories_id=%s" \
                    " and pc.id=p.id";
            cursor.execute(query, str(query_data[0]))
            data_sub = cursor.fetchall()
            product_response_list = []
            for query_data_sub in data_sub:
                product_response = {}
                product_response['ID'] = str(query_data_sub[0])
                product_response['NAME'] = query_data_sub[1]
                product_response['IMAGE'] = query_data_sub[2]
                product_response['VIDEOLINK'] = query_data_sub[3]
                product_response_list.append(product_response)

            category_response['product_list'] = product_response_list

            category_list.append(category_response)

    query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f where" \
            " p.newarrival=1 and f.stock=1 and f.status=1 and p.id=f.product_id group by p.id";
    cursor.execute(query)
    data_sub = cursor.fetchall()
    product_response_newarrival = []

    print(len(data_sub))
    if len(data_sub) > 0:
        for query_data_sub in data_sub:
            product_response = {}
            product_response['ID'] = str(query_data_sub[0])
            product_response['NAME'] = query_data_sub[1]
            product_response['IMAGE'] = query_data_sub[2]
            product_response['VIDEOLINK'] = query_data_sub[3]
            product_response['SIZE'] = f'{str(query_data_sub[4])}-{str(query_data_sub[5])}'
            product_response['PRICE'] = f'{str(query_data_sub[6])}-{str(query_data_sub[7])}'
            product_response['DISCOUNT'] = str(query_data_sub[8])
            product_response_newarrival.append(product_response)

    query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f where" \
            " p.topselling=1 and f.stock=1 and f.status=1 and p.id=f.product_id group by p.id";
    cursor.execute(query)
    data_sub_topselling = cursor.fetchall()
    product_response_topselling = []

    print("Total Size")
    print(len(data_sub_topselling))
    if len(data_sub_topselling) > 0:
        for query_data_sub in data_sub_topselling:
            product_response = {}
            product_response['ID'] = str(query_data_sub[0])
            product_response['NAME'] = query_data_sub[1]
            product_response['IMAGE'] = query_data_sub[2]
            product_response['VIDEOLINK'] = query_data_sub[3]
            product_response['SIZE'] = f'{str(query_data_sub[4])}-{str(query_data_sub[5])}'
            product_response['PRICE'] = f'{str(query_data_sub[6])}-{str(query_data_sub[7])}'
            product_response['DISCOUNT'] = str(query_data_sub[8])
            product_response_topselling.append(product_response)

    response = {'status': STATUS, 'message': MESSAGE, 'bannerlist': banner_list, 'materialList': material_list,
                'category_list': category_list, 'product_response_newarrival': product_response_newarrival,
                'product_response_topselling': product_response_topselling}
    response = encrypt(jsonify(response))
    return response  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
