import pymysql
import time
from flask import Flask, Response, request, jsonify, abort, make_response

app = Flask(__name__)

NUM_CHANNELS = 4
FILL_VALUE = 9999.0

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
SERVER_ERROR = 500

MYSQL_HOST = "localhost"
MYSQL_USER = "pynet"
MYSQL_PASS = "pynet"
MYSQL_DB = "pynet_db"

# =============================================================================================================================================================

# METHOD    ENDPOINT            DESCRIPTION                                                 RETURN 

# GET       /data/1234          get all data tied to device                                 list of lists of data rows (sorted by time) [200] or [404]-device doesnt exist
# POST      /data/1234          create data point for device - form: data point             [201] or [400]-bad data
#
# GET       /devices            get list of devices                                         list of device ids (sorted by id) [200]
# POST      /devices            create a device - form: device num + device config          [201] or [400]-bad info
# 
# GET       /devices/1234       get device config                                           list of config items [200] or [404]-device doesnt exist
# POST      /devices/1234       change device config - form: device config                  [201] or [400]-bad data

# =============================================================================================================================================================

# this is mostly for dev purposes (see if there's anything in there.)            
@app.route("/")
def test_connection():
    return "[Pynet] - Connection Successful"

@app.route("/clear")
def clear_database():
    try:
        # connect to database
        db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
        cursor = db.cursor()
    except:
        abort(SERVER_ERROR)

    try:
        sql_delete = "DELETE FROM devices"
        cursor.execute(sql_delete)
        db.commit()
        sql_delete = "DELETE FROM device_data"
        cursor.execute(sql_delete)
        db.commit()
    except:
        db.rollback()
        abort(SERVER_ERROR)

    # disconnect from server
    db.close()

    return make_response('',OK)

@app.route("/devices", methods=['GET', 'POST'])
def device():

    if request.method == 'POST':
        
        try:
            # connect to database
            db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
            cursor = db.cursor()
        except:
            abort(SERVER_ERROR)

        try:
            #check if device is already in database
            not_in_database(int(request.form['device_id']), cursor)
        except:
            abort(BAD_REQUEST)

        try:
            # create insertion statement
            sql_insert = "INSERT INTO devices(device_id, frequency) \
            VALUES ('%d', '%d')" % \
            (
                int(request.form['device_id']), 
                int(request.form['frequency'])
            )
        except:
            abort(BAD_REQUEST)

        try:
            # insert data
            cursor.execute(sql_insert)
            db.commit()

        except:
            db.rollback()
            abort(SERVER_ERROR)

        # disconnect from server
        db.close()

        return make_response('',CREATED)

    else:

        try:
            # connect to database
            db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
            cursor = db.cursor()
        
        except:
            abort(SERVER_ERROR)

        try:
            # get all devices
            sql_select = "SELECT * FROM devices ORDER BY device_id" 
            cursor.execute(sql_select)
            results = cursor.fetchall()
            return_message = {}
            return_message['response'] = []
            for row in results:
                return_message['response'].append(row[0])

        except:
            abort(SERVER_ERROR)

        # disconnect from server
        db.close()

        return make_response(jsonify(return_message),OK)

@app.route("/devices/<int:device_id>", methods=['GET', 'POST'])
def config(device_id):

    if request.method == 'POST':

        try:
            # connect to database
            db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
            cursor = db.cursor()
        
        except:
            abort(SERVER_ERROR)
        
        try:
            #check if device is in database
            is_in_database(device_id, cursor)
        except:
            abort(NOT_FOUND)

        try:
            #update device row
            sql_update = "UPDATE devices SET frequency = %d WHERE device_id = %d" % \
            (int(request.form['frequency']), device_id)
            cursor.execute(sql_update)
            db.commit()
        except:
            abort(SERVER_ERROR)
            db.rollback()

        # disconnect from server
        db.close()

        return make_response('',OK)

    else:

        try:
            # connect to database
            db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
            cursor = db.cursor()
        
        except:
            abort(SERVER_ERROR)
        
        try:
            #check if device is in database
            is_in_database(device_id, cursor)
        except:
            abort(NOT_FOUND)

        try:
            # get all device's data
            sql_select = "SELECT * FROM devices WHERE device_id = " + str(device_id)
            cursor.execute(sql_select)
            result = cursor.fetchone()
            return_message = {}
            return_message['response'] = result

        except:
            #should never reach this code
            abort(SERVER_ERROR)

        # disconnect from server
        db.close()

        #return jsonify(return_message), OK
        return make_response(jsonify(return_message), OK)

@app.route("/data/<int:device_id>", methods=['GET', 'POST'])
def data(device_id):

    if request.method == 'POST':

        try:
            # connect to database
            db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
            cursor = db.cursor()
        
        except:
            abort(SERVER_ERROR)
        
        try:
            #check if device is in database
            is_in_database(device_id, cursor)
        except:
            abort(NOT_FOUND)

        try:
            # create insertion statement
            sql_insert = "INSERT INTO device_data(device_id, \
            time_stamp, chan_0, chan_1, chan_2, chan_3) \
            VALUES ('%d', '%d', '%f', '%f', '%f', '%f' )" % \
            (
                device_id, 
                int(time.time()), 
                float(request.form['ch0']), 
                float(request.form['ch1']), 
                float(request.form['ch2']), 
                float(request.form['ch3'])
            )
        except:
            abort(BAD_REQUEST)

        try:
            # insert data or except
            cursor.execute(sql_insert)
            db.commit()

        except:
            db.rollback()
            abort(BAD_REQUEST)

        # disconnect from server
        db.close()

        return make_response('', CREATED)

    else:

        try:
            # connect to database
            db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
            cursor = db.cursor()
        
        except:
            abort(SERVER_ERROR)

        try:
            #check if device is not in database
            is_in_database(device_id, cursor)
        except:
            abort(NOT_FOUND)

        
        try:
            # get all device's data
            sql_select = "SELECT * FROM device_data WHERE device_id = " + str(device_id) + " ORDER BY time_stamp" 
            cursor.execute(sql_select)
            results = cursor.fetchall()
            return_message = {}
            return_message['response'] = []
            for row in results:
                return_message['response'].append(row)

        except:
            #should never reach this code
            abort(SERVER_ERROR)

        # disconnect from server
        db.close()

        #return jsonify(return_message), OK
        return make_response(jsonify(return_message), OK)

# raise exception if device_id does not exist
def is_in_database(device_id, cursor):
    sql_select = "SELECT * FROM devices WHERE device_id = " + str(device_id) 
    cursor.execute(sql_select)
    row_count = cursor.rowcount
    if row_count == 0:
        raise Exception()

# raise exception if device_id does exist 
def not_in_database(device_id, cursor):
    sql_select = "SELECT * FROM devices WHERE device_id = " + str(device_id) 
    cursor.execute(sql_select)
    row_count = cursor.rowcount
    if row_count != 0:
        raise Exception()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
