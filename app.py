'''
Database Connection and Configuration for Doctor AI 
'''
try:
    # Necessary Imports
    import sys
    import mysql.connector as mysqldb
    import flask
    import pandas as pd
    from flask_cors import CORS
    from flask import request, jsonify, render_template
    from math import radians, sin, cos, acos
    
    # print("All the Modules are Successfully Imported")
except Exception as e:
    # PLEASE IMPORT THE MODULES FIRST
    print("Enable to import all the necessary Modules---", e)
    sys.exit()

class DBConfigure():
    ''' Constructor Initialization '''
    def __init__(self):
        self.mysqldb = mysqldb

    def __str__(self):
        return self.__class__.__name__

    def db_conn(self):
        ''' DataBase Connection '''
        try:
            conn = self.mysqldb.connect(host="localhost",port=3306, database="location_tracker", user="root", password="Qwerty@1", autocommit=True)    # Local
        except Exception as err:
            conn = self.mysqldb.connect(host="localhost",port=3306, database="location_tracker", user="root", password="bemylife0510", autocommit=True)    # Local
            print(err)
        return conn


app = flask.Flask(__name__, template_folder='templates')
app.config["DEBUG"] = True
CORS(app)

@app.route("/", methods=['GET', 'POST'])
def index1():
    print(request.json)
    return jsonify({"success":"true"})

@app.route('/carpool')
def hello_name():
   return render_template('index.html')

@app.route('/result.html')
def hello():
   return render_template('result.html')


@app.route('/insert', methods=['GET', 'POST'])
def index():
    conn = DBConfigure().db_conn()
    cur = conn.cursor()

    name = request.json['name']
    mobile = request.json['mobile']
    latitude = request.json['lat']
    longitude = request.json['long']
    token = request.json['token']

    cur.execute("select * from valid_tokens where token = '{}'".format(token))

    if len(cur.fetchall()) > 0:
        cur.execute("select * from user_lat_long where mobile = '{}'".format(mobile))
        _data = cur.fetchall()

        if len(_data) == 0:
            cur.execute("Insert into user_lat_long (name, latitude, longitude, mobile, access_token) Values (%s, %s, %s, %s, %s)", [name, latitude, longitude, mobile, token])
        else:
            cur.execute("Update user_lat_long SET name = %s, latitude = %s, longitude = %s , access_token = %s where mobile = %s", [name, latitude, longitude, token, mobile])


        slat = radians(float(latitude))
        slon = radians(float(longitude))

        df = pd.read_sql_query("select * from user_lat_long where mobile != '{}' and access_token = '{}'".format(mobile, token), conn)
        print(df)
        distance = []
        for val in df.values.tolist():
            elat = radians(float(val[3]))
            elon = radians(float(val[4]))

            dist = 1.60934 * 6371.01 * acos(sin(slat)*sin(elat) + cos(slat)*cos(elat)*cos(slon - elon))

            distance.append(dist)

        df['distance_in_miles'] = distance

        df.sort_values(by=['distance_in_miles'], inplace=True)

        print(df)

        data = [{'mobile':_data[1], 'distance':_data[2]} for _data in df[['name', 'mobile', 'distance_in_miles']].values.tolist()]

        return jsonify(data)
    else:
        return jsonify({'success':'false', 'text':'Please enter the valid token'})

