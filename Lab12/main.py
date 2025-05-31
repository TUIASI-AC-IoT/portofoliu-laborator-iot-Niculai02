from flask import Flask, request, jsonify
from flasgger import Swagger
import os
import random
import json

app = Flask(__name__)
swagger = Swagger(app)

SENSOR_IDS = ['sensor1', 'sensor2', 'sensor3']
CONFIG_DIR = 'sensor_configs'
os.makedirs(CONFIG_DIR, exist_ok=True)

def config_path(sensor_id, filename='config.json'):
    return os.path.join(CONFIG_DIR, f"{sensor_id}_{filename}")

def read_sensor(sensor_id):
    scale = 1.0
    config_file = config_path(sensor_id)
    if os.path.exists(config_file):
        with open(config_file) as f:
            config = json.load(f)
            scale = config.get('scale', 1.0)
    value = random.uniform(0, 100) * scale
    return round(value, 2)

@app.route('/sensors/<sensor_id>', methods=['GET'])
def get_sensor_value(sensor_id):
    if sensor_id not in SENSOR_IDS:
        return jsonify({'error': 'Sensor not found'}), 404
    value = read_sensor(sensor_id)
    return jsonify({'sensor_id': sensor_id, 'value': value})

@app.route('/sensors/<sensor_id>/config', methods=['POST'])
def create_sensor_config(sensor_id):
    if sensor_id not in SENSOR_IDS:
        return jsonify({'error': 'Sensor not found'}), 404

    config_file = config_path(sensor_id)
    if os.path.exists(config_file):
        return jsonify({'error': 'Config already exists'}), 409

    data = request.get_json()
    if not data or 'scale' not in data:
        return jsonify({'error': 'Missing scale in request body'}), 400

    config = {'scale': data['scale']}
    with open(config_file, 'w') as f:
        json.dump(config, f)

    return jsonify({'message': 'Config created', 'config': config}), 201

@app.route('/sensors/<sensor_id>/config/<filename>', methods=['PUT'])
def update_sensor_config(sensor_id, filename):
    if sensor_id not in SENSOR_IDS:
        return jsonify({'error': 'Sensor not found'}), 404

    fullpath_and_name = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(fullpath_and_name):
        return jsonify({'error': 'Config does not exist'}), 409

    data = request.get_json()
    if not data or 'scale' not in data:
        return jsonify({'error': 'Missing scale in request body'}), 400

    config = {'scale': data['scale']}
    with open(fullpath_and_name, 'w') as f:
        json.dump(config, f)

    return jsonify({'message': 'Config updated', 'config': config})

if __name__ == '__main__':
    app.run(debug=True)
