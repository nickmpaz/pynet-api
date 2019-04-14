import pymysql
from flask import Flask, request

app = Flask(__name__)



NUM_CHANNELS = 4
 
@app.route("/<int:device_id>")
def store(device_id):
    chan_data = []
    for i in range (NUM_CHANNELS):
        chan_data.append(request.args.get(str(i), type=float))

    return str(chan_data[0]) + " " + str(chan_data[1]) + " " + str(chan_data[2]) + " " + str(chan_data[3])
    



        




@app.route("/")
def test1():
    return "<h1>root</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
