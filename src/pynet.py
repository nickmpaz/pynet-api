import pymysql
import time
from flask import Flask, request

app = Flask(__name__)

NUM_CHANNELS = 4
FILL_VALUE = 9999.0
MYSQL_HOST = "localhost"
MYSQL_USER = "pynet"
MYSQL_PASS = "pynet"
MYSQL_DB = "pynet_db"
 
@app.route("/<int:device_id>", methods=['GET', 'POST'])
def device(device_id):

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

        # insert data
        try:
            cursor.execute(sql_insert)
            db.commit()
            return_message = "1"
        except:
            db.rollback()
            return_message = "0"

        # disconnect from server
        db.close()

        return return_message

    else:

        # connect to database
        db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
        cursor = db.cursor()

        sql_select = "SELECT * FROM device_data WHERE device_id = " + str(device_id)

        try:
            cursor.execute(sql_select)
            results = cursor.fetchall()
            return_message = ""
            for row in results:
                return_message = return_message +  '   '.join([str(elem) for elem in row]) + "\n"

        except:
            return_message = "Error"
        
        return return_message
            

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
