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

# METHOD    ENDPOINT            DESCRIPTION                                                 RETURN 

# GET       /data/1234          get all data tied to device                                 list of lists of data rows (sorted by time) [200] or [404]-device doesnt exist
# POST      /data/1234          create data point for device - form: data point             [201] or [400]-bad data
#
# GET       /devices            get list of devices                                         list of device ids (sorted by id) [200]
# POST      /devices            create a device - form: device num + device config          [201] or [400]-bad info
# 
# GET       /devices/1234       get device config                                           list of config items [200] or [404]-device doesnt exist
# POST      /devices/1234       change device config - form: device config                  [201] or [400]-bad data

@app.route("/devices", methods=['GET', 'POST'])
def device():

    if request.method == 'POST':
        
        # connect to database
        try:
            db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
            cursor = db.cursor()
        except:
            abort(SERVER_ERROR)

        #check if device is already in database
        try:
            is_in_database(int(request.form['device_id']), cursor)
        except:
            abort(BAD_REQUEST)

        # create insertion statement
        try:
            sql_insert = "INSERT INTO devices(device_id, frequency) \
            VALUES ('%d', '%d')" % \
            (
                int(request.form['device_id']), 
                int(request.form['frequency'])
            )
        except:
            abort(BAD_REQUEST)

        # insert data
        try:
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
            sql_select = "SELECT * FROM devices" 
            cursor.execute(sql_select)
            results = cursor.fetchall()
            return_message = {}
            return_message['response'] = []
            for row in results:
                return_message['response'].append(row[0])

        except:
            abort(SERVER_ERROR)

        return make_response(jsonify(return_message),OK)

@app.route("/data/<int:device_id>", methods=['GET', 'POST'])
def data(device_id):

    if request.method == 'POST':

        # connect to database
        db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
        cursor = db.cursor()

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

        # insert data or except
        try:
            cursor.execute(sql_insert)
            db.commit()

        except:
            db.rollback()
            abort(BAD_REQUEST)

        # disconnect from server
        db.close()

        return CREATED

    #FIXME maybe this should return data in order by time... change the sql stuff
    else:

        # connect to database
        db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
        cursor = db.cursor()

        #check if device is in database
        sql_select = "SELECT * FROM devices WHERE device_id = " + str(device_id)
        try:
            cursor.execute(sql_select)
            row_count = cursor.rowcount
            if row_count == 0:
                abort(NOT_FOUND)

        except:
            abort(BAD_REQUEST)

        # get all device's data
        sql_select = "SELECT * FROM device_data WHERE device_id = " + str(device_id) + " ORDER BY time_stamp" 
        try:
            cursor.execute(sql_select)
            results = cursor.fetchall()
            return_message = {}
            return_message['response'] = []
            for row in results:
                return_message['response'].append(row)

        except:
            #should never reach this code
            pass

        #return jsonify(return_message), OK
        return jsonify(return_message)
            

# this is mostly for dev purposes (see if there's anything in there.)            
@app.route("/")
def dataNum():
    db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
    cursor = db.cursor()

    sql_select = "SELECT COUNT(*) FROM device_data"

    try:
        cursor.execute(sql_select)
        results = cursor.fetchall()
        return_message = "rows in device_data: "
        for row in results:
            return_message = return_message +  '   '.join([str(elem) for elem in row]) + "\n"

    except:
        return_message = "Error"
        
    return return_message

def is_in_database(device_id, cursor):
    # get all devices
    sql_select = "SELECT * FROM devices" 
    cursor.execute(sql_select)
    results = cursor.fetchall()
    for row in results:
        if row[0] == device_id:
            raise Exception()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
