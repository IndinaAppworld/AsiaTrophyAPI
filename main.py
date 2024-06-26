# This is a sample Python script.
import random
import string
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
    r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return "".join([r] + d)


def encrypt(str):
    return str;


def decrypt(str):
    return str;


def generate_otp(length=4):
    """Generate a random OTP"""
    return ''.join(random.choices(string.digits, k=length))




@app.route('/api/processorder', methods=['POST'])
def process_order():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    CUSTOMERID = data.get('CUSTOMERID')
    TOTALPRICE = data.get('TOTALPRICE')
    DISCOUNTEDPRICE = data.get('DISCOUNTEDPRICE')
    STATUS = True
    MESSAGE = "Transaction Success"
    ORDERID=""
    # items = data.get('items')  # Assuming items is a list of dictionaries

    try:
        cursor = mysql.get_db().cursor()
        current_time = datetime.now()

        # Process the order items
        insert_order_query = "INSERT INTO asiatrophybackend_order (customer_id, total_price, discounted_price, order_date,created_at,created_by,status,comments) VALUES (%s, %s, %s, %s,%s, %s, %s, %s)"
        # order_values = (
        cursor.execute(insert_order_query, (CUSTOMERID,TOTALPRICE,DISCOUNTEDPRICE,current_time,current_time,'Customer','1','Order Created'))

        ORDERID = cursor.lastrowid
        print(ORDERID)
        # order_id = cursor.lastrowid  # Get the ID of the inserted order
        #
        # # Insert order item data into the 'order_items' table
        for item in data['items']:
            insert_item_query = "INSERT INTO asiatrophybackend_orderitem (order_id, flavour_id, product_id,quantity, price,discount_percent,price_discount,total_price,total_price_discount) VALUES (%s, %s, %s, %s, %s, %s, %s,%s,%s)"
            item_values = (ORDERID, item['flavour_id'],item['product_id'], item['quantity'], item['price'],item['discount_percent'],item['price_discount'],
                           item['total_price'],item['total_price_discount'])
            cursor.execute(insert_item_query, item_values)

        cursor.connection.commit()
        cursor.close()

    # Example response with extracted order information
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,'orderid':str(ORDERID)}

    return response

@app.route('/api/verifyotp', methods=['POST'])
def verify_otp():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    OTP = data.get('OTP')

    STATUS = True
    MESSAGE = "Transaction Success"
    PI = {}

    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("""
            SELECT otp, created_at, is_valid
            FROM otps
            WHERE mobile_number = %s
        """, (MOBILENO,))
        result = cursor.fetchone()

        if result:
            stored_otp, created_at, is_valid = result
            if is_valid == 0:
                STATUS=False
                MESSAGE = "OTP has already been used or is invalid"
            else:
                current_time = datetime.now()
                if stored_otp == OTP and (current_time - created_at).seconds <= 600:  # 5 minutes validity
                    cursor.execute("""
                        UPDATE otps
                        SET is_valid = 0
                        WHERE mobile_number = %s AND otp = %s
                    """, (MOBILENO, OTP))
                    cursor.connection.commit()

                    MESSAGE = "OTP has been verified Successfully!"
                    cursor.execute("""
                                SELECT custid, custname,shopname,type,emailid,discountamt_self
                                FROM asiatrophybackend_b2bcustomer
                                WHERE mobileno = %s
                            """, (MOBILENO,))
                    result = cursor.fetchone()
                    if result:
                        last_login = datetime.now()
                        cursor.execute("""
                            UPDATE asiatrophybackend_b2bcustomer
                            SET lastlogin = %s
                            WHERE mobileno = %s
                        """, (last_login, MOBILENO,))
                        cursor.connection.commit()

                        PI['CUSTID'] = result[0]
                        print(result[0])
                        print(result[1])

                        PI['NAME'] = result[1]
                        PI['SHOPNAME'] = result[2]
                        PI['TYPE'] = result[3]
                        PI['EMAILID'] = result[4]
                        PI['DISCOUNT']=result[5]
                    else:
                        last_login = datetime.now()
                        cursor.execute("""
                                        INSERT INTO asiatrophybackend_b2bcustomer (custname,mobileno,shopname,type,emailid,
                                        discountamt_self,status,lastlogin)
                                        VALUES ('',%s,'',2,'', 0.0, 1,%s)
                
                         """, (MOBILENO, last_login))
                        cursor.connection.commit()

                        cursor.execute(""" SELECT custid  from asiatrophybackend_b2bcustomer where mobileno = %s
                                                    """, (MOBILENO))
                        result = cursor.fetchone()

                        print("RESULT----_>")
                        print((result[0]))

                        if result:
                            print(result[0])
                            PI['CUSTID'] = str(result[0])

                        PI['NAME'] = ''
                        PI['SHOPNAME'] = ''
                        PI['TYPE'] = '2'
                        PI['EMAILID'] = ''
                        PI['ADDRESS'] = ''
                        PI['DISCOUNT']=0

                    cursor.close()

                else:
                    MESSAGE = "Invalid or expired OTP"
                    STATUS=False
        else:
            MESSAGE = "No OTP found for this mobile number"
            STATUS=False
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE, 'PI': PI}

    return response


@app.route('/api/addaddress', methods=['POST'])
def add_address():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    CUSTOMERID = data.get('CUSTOMERID')
    ADDRESS = data.get('ADDRESS')
    CITY = data.get('CITY')
    STATE = data.get('STATE')
    PINCODE = data.get('PINCODE')
    COUNTRY = data.get('COUNTRY')
    TYPE = data.get('TYPE')

    STATUS = True
    MESSAGE = "Address has been added Successfully!"

    try:
        current_time = datetime.now()
        cursor = mysql.get_db().cursor()
        cursor.execute("""
            INSERT INTO asiatrophybackend_address (customer_id, address, city, state, zip_code, type,country,createdat,updatedat)
            VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)
        """, (CUSTOMERID, ADDRESS, CITY, STATE, PINCODE, TYPE, COUNTRY, current_time, current_time))
        cursor.connection.commit()
        cursor.close()

    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE}

    return response

@app.route('/api/deleteaddress', methods=['POST'])
def delete_address():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    ADDRESS_ID = data.get('ADDRESS_ID')
    CUSTOMERID = data.get('CUSTOMERID')
    STATUS = True
    MESSAGE = "Address has been deleted successfully!"

    try:
        cursor = mysql.get_db().cursor()
        result=cursor.execute("DELETE FROM asiatrophybackend_address WHERE address_id = %s and customer_id=%s", (ADDRESS_ID,CUSTOMERID))
        print(result)
        cursor.connection.commit()
        cursor.close()

        if result==0:
            STATUS = False
            MESSAGE = "Address Delete Request has been Failed!"


    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE}

    return jsonify(response)


@app.route('/api/orderdetailslist', methods=['POST'])
def orderDetailsList():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    CUSTOMERID = data.get('CUSTOMERID')
    ORDERID = data.get('ORDERID')
    STATUS = True
    MESSAGE = "Order Details Fetch successfully!"
    orderDetailsList = []

    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("""
              SELECT oi.id, oi.quantity, oi.flavour_id,oi.order_id,oi.product_id,oi.discount_percent,oi.price,oi.price_discount, oi.total_price,oi.total_price_discount,
              f.size, p.name,p.image
              
               from asiatrophybackend_orderitem oi,asiatrophybackend_flavor f,asiatrophybackend_product p
              WHERE oi.order_id = %s and oi.product_id=p.id and oi.flavour_id=f.id
          """, (ORDERID,))
        order_data = cursor.fetchall()

        if len(order_data) > 0:
            for order in order_data:
                order_response = {}
                order_response['id'] = str(order[0])
                order_response['quantity'] = str(order[1])
                order_response['flavour_id'] = str(order[2])
                order_response['order_id'] = str(order[3])
                order_response['product_id'] = str(order[4])
                order_response['discount_percent'] = str(order[5])
                order_response['price'] = str(order[6])
                order_response['price_discount'] = str(order[7])
                order_response['total_price'] = str(order[8])
                order_response['total_price_discount'] = str(order[9])
                order_response['size'] = str(order[10])
                order_response['pname'] = str(order[11])
                order_response['pimage'] = str(order[12])

                orderDetailsList.append(order_response)
        else:
            MESSAGE = "No Order Details Found!"
            orderDetailsList = []
        cursor.close()

    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    # Custom JSON key for the list of addresses
    response = {'status': STATUS, 'message': MESSAGE, 'orderDetailsList': orderDetailsList}

    return response

@app.route('/api/orderlist', methods=['POST'])
def orderList():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    CUSTOMERID = data.get('CUSTOMERID')
    ORDERSTATUS=data.get('ORDERSTATUS')
    STATUS = True
    MESSAGE = "Order Fetch successfully!"
    orderList = []

    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("""
              SELECT orderid, order_date, status, discounted_price, total_price
              FROM asiatrophybackend_order
              WHERE customer_id = %s
          """, (CUSTOMERID,))
        order_data = cursor.fetchall()

        if len(order_data) > 0:
            for order in order_data:
                order_response = {}
                order_response['orderid'] = str(order[0])
                order_response['orderdate'] = order[1].strftime('%d-%B-%Y %I:%M %p')
                order_response['orderstatus'] = order[2]
                order_response['discounted_price'] = str(order[3])
                order_response['total_price'] = str(order[4])
                orderList.append(order_response)
        else:
            MESSAGE = "No Order Found!"
            orderList = []
        cursor.close()

    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    # Custom JSON key for the list of addresses
    response = {'status': STATUS, 'message': MESSAGE, 'orderlist': orderList}

    return response

@app.route('/api/addresslist', methods=['POST'])
def get_addresses():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    CUSTOMERID = data.get('CUSTOMERID')
    STATUS = True
    MESSAGE = "Addresses retrieved successfully!"
    addresses = []

    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("""
            SELECT address_id, address, city, state, zip_code, country,type
            FROM asiatrophybackend_address
            WHERE customer_id = %s
        """, (CUSTOMERID,))
        addresses_data = cursor.fetchall()
        cursor.close()

        if  len(addresses_data)>0:
            for address in addresses_data:
                address_response={}
                address_response['addresses_id'] = address[0]
                address_response['addresses'] = address[1]
                address_response['city'] = address[2]
                address_response['state'] = address[3]
                address_response['zip_code'] = address[4]
                address_response['country'] = address[5]
                address_response['type'] = address[6]
                addresses.append(address_response)
        else:
            STATUS = False
            MESSAGE = "No Address Details has been provided. Click on (+) icon to add your Address Information."


    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    # Custom JSON key for the list of addresses
    response = {'status': STATUS, 'message': MESSAGE, 'address': addresses}

    return response



@app.route('/api/updateaddress', methods=['POST'])
def update_address():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    ADDRESS_ID = data.get('ADDRESS_ID')
    CUSTOMERID = data.get('CUSTOMERID')
    ADDRESS = data.get('ADDRESS')
    CITY = data.get('CITY')
    STATE = data.get('STATE')
    PINCODE = data.get('PINCODE')
    COUNTRY = data.get('COUNTRY')
    TYPE = data.get('TYPE')

    STATUS = True
    MESSAGE = "Address has been updated successfully!"

    try:
        current_time = datetime.now()
        cursor = mysql.get_db().cursor()
        cursor.execute("""
            UPDATE asiatrophybackend_address
            SET customer_id = %s, address = %s, city = %s, state = %s, zip_code = %s, type = %s, country = %s, updatedat = %s
            WHERE address_id = %s and customer_id=%s
        """, (CUSTOMERID, ADDRESS, CITY, STATE, PINCODE, TYPE, COUNTRY, current_time, ADDRESS_ID,CUSTOMERID))
        cursor.connection.commit()
        cursor.close()

    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE}

    return response


@app.route('/api/updatecustomer', methods=['POST'])
def update_customer():

    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    NAME = data.get('NAME')
    CUSTOMERID = data.get('CUSTOMERID')
    SHOPNAME = data.get('SHOPNAME')

    print(MOBILENO)

    STATUS = True
    MESSAGE = "Datails have been updated successfully!"

    try:
        cursor = mysql.get_db().cursor()
        result=cursor.execute("""
            UPDATE asiatrophybackend_b2bcustomer
            SET custname = %s, shopname = %s
            WHERE custid = %s
        """, (NAME, SHOPNAME, CUSTOMERID))
        cursor.connection.commit()
        cursor.close()

        if result==0:
            STATUS = False
            MESSAGE = "Failed to Update the details!"

    except Exception as e:
            STATUS = False
            MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE}

    return response


@app.route('/api/generateotp', methods=['POST'])
def generate_otp_for_mobile():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    print(MOBILENO)

    STATUS = True
    MESSAGE = "Transaction Success"

    try:
        otp = generate_otp()
        otp_created_at = datetime.now()
        cursor = mysql.get_db().cursor()
        cursor.execute("SELECT * FROM otps WHERE mobile_number = %s", (MOBILENO,))
        result = cursor.fetchone()

        if result:
            # Update the existing record
            cursor.execute("""
                UPDATE otps
                SET otp = %s, created_at = %s, is_valid = 1
                WHERE mobile_number = %s
            """, (otp, otp_created_at, MOBILENO))
        else:
            # Insert a new record
            cursor.execute("""
                INSERT INTO otps (mobile_number, otp, created_at, is_valid)
                VALUES (%s, %s, %s, 1)
            """, (MOBILENO, otp, otp_created_at))

        cursor.connection.commit()


    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE}

    return response


@app.route('/api/filtermaster', methods=['POST'])
async def filtermaster():
    data = request.form['data']
    data = decrypt(data)
    customPrint(data)
    data = json.loads(data)
    MOBILENO = data.get('MOBILENO')

    category_list = []
    material_list = []
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

        query = "select id,name from asiatrophybackend_material where status=1";
        cursor.execute(query)
        data = cursor.fetchall()
        if len(data) > 0:
            for query_data in data:
                allmaterial_response = {}
                allmaterial_response['ID'] = str(query_data[0])
                allmaterial_response['NAME'] = query_data[1]
                material_list.append(allmaterial_response)


    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,
                'category_list': category_list, 'material_list': material_list}
    response = encrypt(jsonify(response))
    return response


@app.route('/api/allcategories', methods=['POST'])
async def allcategories():
    data = request.form['data']
    customPrint(data)
    data = json.loads(data)
    data = data.get('data')
    data = decrypt(data)
    MOBILENO = data.get('MOBILENO')
    print("***********************");
    print(MOBILENO)
    print("***********************");

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
    CATEGORYID = data.get('CATEGORYID')
    TOPSELLING = data.get('TOPSELLING')
    NEWARRIVAL = data.get('NEWARRIVAL')
    OFFERS = data.get('OFFERS')
    MINPRICE = data.get('MINPRICE')
    MAXPRICE = data.get('MAXPRICE')

    customPrint(MATERIALID)
    customPrint(MOBILENO)
    customPrint(CATEGORYID)

    product_list = []
    STATUS = True
    MESSAGE = "Transaction Success"
    query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f, asiatrophybackend_product_categories pc where p.status=1 and f.product_id=p.id";

    try:
        cursor = mysql.get_db().cursor()

        # "group by p.id"
        if len(MATERIALID) > 0:
            query = query + " and p.material_id in (" + MATERIALID + ")";

        if len(CATEGORYID) > 0:
            query = query + " and pc.categories_id in (" + CATEGORYID + ") and pc.product_id=p.id";

        if len(TOPSELLING) > 0:
            query = query + " and topselling=1";

        if len(NEWARRIVAL) > 0:
            query = query + " and newarrival=1";

        if len(OFFERS) > 0:
            query = query + " and offers=1";

        if len(MINPRICE) > 0:
            query = query + " and f.price>=" + (MINPRICE);

        if len(MAXPRICE) > 0:
            query = query + " and f.price<=" + (MAXPRICE);

        query = query + " group by p.id"

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
                product_response[
                    'PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_list.append(product_response)
        else:
            STATUS = False
            MESSAGE = "No Product Found!"
    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE,
                'product_list': product_list, 'pcount': len(product_list)}
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
    CATEGORYID = data.get('CATEGORYID')
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

        if len(MATERIALID) > 0:
            query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f where f.stock=1 and f.status=1 and p.id=f.product_id and p.material_id in (" + MATERIALID + ") group by p.id";
            customPrint(query)
            customPrint(query)  # Print the query with parameters substituted
            cursor.execute(query)
            # formatted_query = query % MATERIALID  # Format the query with placeholders

            data_sub = cursor.fetchall()
            print("TOTAL RECORD>>>>>")
            print(len(data_sub))

        elif len(CATEGORYID) > 0:
            query = "select p.id,p.name,p.image,p.videolink,min(f.size),max(f.size),min(f.price),max(f.price),max(f.discount) from  asiatrophybackend_product p, asiatrophybackend_flavor f,asiatrophybackend_product_categories pc where f.stock=1 and f.status=1 and p.id=f.product_id and pc.categories_id in (" + CATEGORYID + ") and pc.product_id=p.id group by p.id";
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
                product_response[
                    'PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
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

                query_flavour = "select f.id,f.size,f.image,f.price,f.discount,f.product_id,f.stock,f.quantity,f.discountamount from  asiatrophybackend_flavor f where" \
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

                    if query_data_flavour[8] is None:
                        flavour_response['DISCOUNTAMOUNT'] =0
                    else:
                        flavour_response['DISCOUNTAMOUNT'] = float(query_data_flavour[8])

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
    product_response_offers = []

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
                product_response[
                    'PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
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
                product_response[
                    'PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
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
                product_response[
                    'PRICE'] = f'₹. {formatINR(str(query_data_sub[6]))} - ₹. {formatINR(str(query_data_sub[7]))}'
                product_response['DISCOUNT'] = str(query_data_sub[8])
                product_response_offers.append(product_response)

    except Exception as e:
        STATUS = False
        MESSAGE = "APPLICATION ERROR-->" + str(e)

    response = {'status': STATUS, 'message': MESSAGE, 'bannerlist': banner_list, 'materialList': material_list,
                'category_list': category_list, 'product_response_newarrival': product_response_newarrival,
                'product_response_topselling': product_response_topselling,
                'product_response_offers': product_response_offers}
    response = encrypt(jsonify(response))
    return response  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
