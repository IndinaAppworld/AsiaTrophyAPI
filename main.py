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

def formatINR(number):
    s, *d = (number).partition(".")
    r = ",".join([s[x-2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return "".join([r] + d)


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
@app.route('/api/allcategories', methods=['POST'])
async def allcategories():
    data = request.form['data']
    data = decrypt(data)
    customPrint(data)
    data = json.loads(data)
    MOBILENO = data.get('MOBILENO')

    category_list = []
    STATUS = True
    MESSAGE = "Transaction Success"

    try:
        cursor = mysql.get_db().cursor()
        query = "select id,name,image from asiatrophybackend_categories where status=1";
        cursor.execute(query)
        data = cursor.fetchall()
        if len(data) > 0:
            for query_data in data:
                category_response = {}
                category_response['ID'] = str(query_data[0])
                category_response['NAME'] = query_data[1]
                category_response['IMAGE'] = query_data[2]
                category_list.append(category_response)
        else:
            STATUS = False
            MESSAGE = "No Category Found!"
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,
                'category_list': category_list}
    response = encrypt(jsonify(response))
    return response

@app.route('/api/productlistnew', methods=['POST'])
async def productlistNew():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    MATERIALID = data.get('MATERIALID')
    CATEGORYID=data.get('CATEGORYID')
    TOPSELLING = data.get('TOPSELLING')
    NEWARRIVAL = data.get('NEWARRIVAL')
    OFFERS = data.get('OFFERS')

    customPrint(MATERIALID)
    customPrint(MOBILENO)
    customPrint(CATEGORYID)


    product_list = []
    STATUS = True
    MESSAGE = "Transaction Success"
    query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f where p.status=1";

    try:
        cursor = mysql.get_db().cursor()

        # "group by p.id"
        if  len(MATERIALID)>0:
            query = query+ " and p.material_id in ("+MATERIALID+")";

        if len(CATEGORYID)>0:
            query = query + " and pc.categories_id in ("+CATEGORYID+") and pc.product_id=p.id";

        if len(TOPSELLING) > 0:
            query = query + " and topselling=1";

        if len(NEWARRIVAL) > 0:
            query = query + " and newarrival=1";

        if len(OFFERS) > 0:
            query = query + " and offers=1";

        query=query+" group by p.id"
        print(query)
        cursor.execute(query)
        data_sub = cursor.fetchall()
        print(len(data_sub))


        if len(data_sub) > 0:
            for query_data_sub in data_sub:
                product_response = {}
                product_response['ID'] = str(query_data_sub[0])
                product_response['NAME'] = query_data_sub[1]
                product_response['IMAGE'] = query_data_sub[2]
                product_response['VIDEOLINK'] = query_data_sub[3]
                product_response['SIZE'] = f'{str(query_data_sub[4])} in -{str(query_data_sub[5])} in'
                product_response['PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_list.append(product_response)
        else:
            STATUS = False
            MESSAGE = "No Product Found!"
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,
                'product_list': product_list}
    response = encrypt(jsonify(response))
    return response




@app.route('/api/productlist', methods=['POST'])
async def productlist():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    MATERIALID = data.get('MATERIALID')
    CATEGORYID=data.get('CATEGORYID')
    TOPSELLING = data.get('TOPSELLING')
    TOPSELLING = data.get('TOPSELLING')

    customPrint(MATERIALID)
    customPrint(MOBILENO)
    customPrint(CATEGORYID)


    product_list = []
    STATUS = True
    MESSAGE = "Transaction Success"

    try:
        cursor = mysql.get_db().cursor()

        if  len(MATERIALID)>0:
            query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f where f.stock=1 and f.status=1 and p.id=f.product_id and p.material_id in ("+MATERIALID+") group by p.id";
            customPrint(query)
            customPrint(query )  # Print the query with parameters substituted
            cursor.execute(query)
            # formatted_query = query % MATERIALID  # Format the query with placeholders

            data_sub = cursor.fetchall()
            print("TOTAL RECORD>>>>>")
            print(len(data_sub))

        elif   len(CATEGORYID)>0:
            query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f,asiatrophybackend_product_categories pc where f.stock=1 and f.status=1 and p.id=f.product_id and pc.categories_id in ("+CATEGORYID+") and pc.product_id=p.id group by p.id";
            customPrint(query)
            cursor.execute(query)
            data_sub = cursor.fetchall()

        elif len(TOPSELLING) > 0:
            query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f,asiatrophybackend_product_categories pc where f.stock=1 and f.status=1 and p.id=f.product_id and p.topselling=1 and pc.product_id=p.id group by p.id";
            customPrint(query)
            cursor.execute(query)
            data_sub = cursor.fetchall()

            print(len(data_sub))

        elif len(TOPSELLING) > 0:
            query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f,asiatrophybackend_product_categories pc where f.stock=1 and f.status=1 and p.id=f.product_id and p.topselling=1 and pc.product_id=p.id group by p.id";
            customPrint(query)
            cursor.execute(query)
            data_sub = cursor.fetchall()

            print(len(data_sub))


        if len(data_sub) > 0:
            for query_data_sub in data_sub:
                product_response = {}
                product_response['ID'] = str(query_data_sub[0])
                product_response['NAME'] = query_data_sub[1]
                product_response['IMAGE'] = query_data_sub[2]
                product_response['VIDEOLINK'] = query_data_sub[3]
                product_response['SIZE'] = f'{str(query_data_sub[4])} in -{str(query_data_sub[5])} in'
                product_response['PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_list.append(product_response)
        else:
            STATUS = False
            MESSAGE = "No Product Found!"
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,
                'product_list': product_list}
    response = encrypt(jsonify(response))
    return response

@app.route('/api/singleproductdetails', methods=['POST'])
async def singleproductdetails():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    PRODUCTID = data.get('PRODUCTID')
    customPrint(PRODUCTID)

    product_details_response = []
    flavour_details_response = []
    STATUS = True
    MESSAGE = "Transaction Success"

    try:
        cursor = mysql.get_db().cursor()
        query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount),p.description,m.name from  asiatrophybackend_product p, asiatrophybackend_flavor f," \
                "asiatrophybackend_material m where" \
                " p.id=%s and p.id=f.product_id and p.material_id=m.id group by p.id";
        cursor.execute(query, PRODUCTID)
        product_details = cursor.fetchall()

        print("Total Size")
        print(len(product_details))
        if len(product_details) > 0:
            for query_data_sub in product_details:
                product_response = {}
                categories_str = ""
                product_response['ID'] = str(query_data_sub[0])
                product_response['NAME'] = query_data_sub[1]
                product_response['IMAGE'] = query_data_sub[2]
                product_response['VIDEOLINK'] = query_data_sub[3]
                product_response['SIZE'] = f'{str(query_data_sub[4])} in -{str(query_data_sub[5])} in'
                product_response['PRICE'] = f'{str(query_data_sub[6])}-{str(query_data_sub[7])}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_response['DESCRIPTION'] = str(query_data_sub[9])
                product_response['MATERIAL'] = str(query_data_sub[10])

                query = "select c.name from asiatrophybackend_categories c,asiatrophybackend_product_categories pc where pc.product_id=%s and pc.categories_id=c.id";
                cursor.execute(query, PRODUCTID)
                product_details_material = cursor.fetchall()
                for categoryname in product_details_material:
                    categories_str = categoryname[0] + "," + categories_str

                if categories_str.endswith(","):
                    categories_str = categories_str[:-1]

                product_response['CATEGORIES'] = str(categories_str)

                query_flavour = "select f.id,f.size,f.image,f.price,f.discount,f.product_id,f.stock,f.quantity from  asiatrophybackend_flavor f where" \
                                " product_id=%s";
                cursor.execute(query_flavour, PRODUCTID)
                product_flavour_details = cursor.fetchall()
                for query_data_flavour in product_flavour_details:
                    flavour_response = {}
                    flavour_response['ID'] = str(query_data_flavour[0])
                    flavour_response['SIZE'] = str(query_data_flavour[1])
                    flavour_response['IMAGE'] = query_data_flavour[2]
                    flavour_response['PRICE'] = str(query_data_flavour[3])
                    flavour_response['DISCOUNT'] = str(query_data_flavour[4])
                    flavour_response['PRODUCT_ID'] = str(query_data_flavour[5])
                    flavour_response['STOCK'] = int(query_data_flavour[6])
                    flavour_response['QTY'] = int(query_data_flavour[7])

                    if None != query_data_flavour[7]:
                        if int(query_data_flavour[7]) < 0:
                            flavour_response['STOCK'] = 0

                    flavour_details_response.append(flavour_response)

                product_response['flavour'] = flavour_details_response;
                product_details_response.append(product_response)
        else:
            STATUS = False
            MESSAGE = "No Details Found!"
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,
                'product_details_response': product_details_response}
    response = encrypt(jsonify(response))
    return response


@app.route('/api/allmaterial', methods=['POST'])
async def allmaterial():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')


    material_list = []
    STATUS = True
    MESSAGE = "Transaction Success"

    try:
        cursor = mysql.get_db().cursor()
        query = "SELECT m.id, m.name, m.image, COUNT(p.id) FROM asiatrophybackend_material m LEFT JOIN " \
                "asiatrophybackend_product p ON m.id = p.material_id WHERE m.status = 1 GROUP BY m.id, m.name, m.image;";
        print(query)
        cursor.execute(query)
        data = cursor.fetchall()
        if len(data) > 0:
            for query_data in data:
                material_response = {}
                material_response['ID'] = str(query_data[0])
                material_response['NAME'] = query_data[1]
                material_response['IMAGE'] = query_data[2]
                material_response['PCOUNT'] = str(query_data[3])

                material_list.append(material_response)
        else:
            STATUS = False
            MESSAGE = "No Category Found!"
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,
                'material_list': material_list}
    response = encrypt(jsonify(response))
    return response


@app.route('/api/dashboard', methods=['POST'])
async def dashboard():
    data = request.form['data']
    data = decrypt(data)
    customPrint(data)
    data = json.loads(data)
    MOBILENO = data.get('MOBILENO')

    banner_list = []
    material_list = []
    category_list = []
    product_response_newarrival = []
    product_response_topselling = []
    product_response_offers=[]

    STATUS = True
    MESSAGE = "Transaction Success"

    try:

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

        print(len(data_sub))
        if len(data_sub) > 0:
            for query_data_sub in data_sub:
                product_response = {}
                product_response['ID'] = str(query_data_sub[0])
                product_response['NAME'] = query_data_sub[1]
                product_response['IMAGE'] = query_data_sub[2]
                product_response['VIDEOLINK'] = query_data_sub[3]
                product_response['SIZE'] = f'{str(query_data_sub[4])} in -{str(query_data_sub[5])} in'
                product_response['PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_response_newarrival.append(product_response)

        query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f where" \
                " p.topselling=1 and f.stock=1 and f.status=1 and p.id=f.product_id group by p.id";
        cursor.execute(query)
        data_sub_topselling = cursor.fetchall()

        print("Total Size")
        print(len(data_sub_topselling))
        if len(data_sub_topselling) > 0:
            for query_data_sub in data_sub_topselling:
                product_response = {}
                product_response['ID'] = str(query_data_sub[0])
                product_response['NAME'] = query_data_sub[1]
                product_response['IMAGE'] = query_data_sub[2]
                product_response['VIDEOLINK'] = query_data_sub[3]
                product_response['SIZE'] = f'{str(query_data_sub[4])} in -{str(query_data_sub[5])} in'
                product_response['PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_response_topselling.append(product_response)

        query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f where" \
                " p.offers=1 and f.stock=1 and f.status=1 and p.id=f.product_id group by p.id";
        cursor.execute(query)
        data_sub = cursor.fetchall()

        print(len(data_sub))
        if len(data_sub) > 0:
            for query_data_sub in data_sub:
                product_response = {}
                product_response['ID'] = str(query_data_sub[0])
                product_response['NAME'] = query_data_sub[1]
                product_response['IMAGE'] = query_data_sub[2]
                product_response['VIDEOLINK'] = query_data_sub[3]
                product_response['SIZE'] = f'{str(query_data_sub[4])} in -{str(query_data_sub[5])} in'
                product_response['PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_response_offers.append(product_response)

    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE, 'bannerlist': banner_list, 'materialList': material_list,
                'category_list': category_list, 'product_response_newarrival': product_response_newarrival,
                'product_response_topselling': product_response_topselling,'product_response_offers':product_response_offers}
    response = encrypt(jsonify(response))
    return response  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
