import pymysql
import time
from flask import Flask, request

app = Flask(__name__)

NUM_CHANNELS = 4
MYSQL_HOST = "localhost"
MYSQL_USER = "pynet"
MYSQL_PASS = "pynet"
MYSQL_DB = "pynet_db"
 
@app.route("/<int:device_id>")
def store(device_id):
    
    # read in query parameters
    chan_data = []
    for i in range (NUM_CHANNELS):
        chan_data.append(request.args.get(str(i), type=float))

    # connect to database
    db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)
    cursor = db.cursor()

    # create insertion statement
    sql_insert = "INSERT INTO device_data(device_id, \
    time_stamp, chan_0, chan_1, chan_2, chan_3) \
    VALUES ('%d', '%d', '%f', '%f', '%f', '%f' )" % \
    (device_id, int(time.time()), chan_data[0], chan_data[1], chan_data[2], chan_data[3])

    try:
        cursor.execute(sql_insert)
        db.commit()
        return_message = "inserted ;)"
    except:
        db.rollback()
        return_message = "didn't insert :("

    # disconnect from server
    db.close()
    return return_message



@app.route("/")
def test1():
    db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASS, MYSQL_DB)

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # execute SQL query using execute() method.
    cursor.execute("SELECT VERSION()")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()

    # disconnect from server
    db.close()
    return "did it ;)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
