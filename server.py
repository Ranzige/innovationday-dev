from flask import Flask, render_template, Response, request
import requests
import json
from urllib2 import HTTPHandler
import rpi.sensor_tag

app = Flask(__name__)

sensor = rpi.sensor_tag.PiSensor()

def combineData(truck, environment):
    truck["environment"] = environment
    jsonData = json.dumps(truck, indent=4, sort_keys=True, ensure_ascii=False)
    jsonData = eval(jsonData)
    #jsonData  = json.loads(jsonData)
    return jsonData

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/init', methods=['POST'])
def init_start():

    environment = sensor.getEnv()


    container = request.form.getlist('container[]')
    deliveryman = request.form['deliveryman']
    vehicle = request.form.getlist('vehicle[]')
    driver = request.form.getlist('driver[]')
    path = request.form.getlist('path[]')
    batch = request.form['batch']
    order = request.form['order']
    target = request.form['target']
    start = request.form['start']

    result = {
        "batch": batch,
        "container": container,
        "deliveryman":deliveryman,
        "order": order,
        "vehicle": vehicle,
        "driver":driver,
        "target": target,
        "start": start,
        "path":path
    }

    data = combineData(result,environment)
    sensor.sendMQTT(data)
    resp = Response(json.dumps(data), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

@app.route('/initWay', methods=['POST'])
def init_way():

    environment = sensor.getEnv()

    container = request.form.getlist('container[]')
    deliveryman = request.form['deliveryman']
    vehicle = request.form.getlist('vehicle[]')
    driver = request.form.getlist('driver[]')
    batch = request.form['batch']
    order = request.form['order']
    location = request.form['location']
    result = {
        'batch': batch,
        'container': container,
        'deliveryman': deliveryman,
        'order': order,
        'vehicle': vehicle,
        'driver': driver,
        'location': location
    }

    data = combineData(result,environment)
    sensor.sendMQTTStart(data)
    resp = Response(json.dumps(data), mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
