from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__)
CORS(app)

# Хранилище данных
current_data = {
    "temperature": -99,
    "humidity": -99,
    "soil_moisture": -99,
    "light_level": -99,
    "last_update": "не обновлялось",
    "devices": {
        "vent": False,
        "fan": False,
        "heater": False,
        "light": False,
        "pump": False
    }
}
history = []
MAX_HISTORY = 100


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        print(f" Получены RAW данные: {data}")
        
        if data:
            processed_data = {
                "temperature": float(data.get('temperature', -99)),
                "humidity": float(data.get('humidity', -99)),
                "soil_moisture": int(data.get('soil_moisture', -99)),
                "light_level": int(data.get('light_level', -99)),
                "last_update": datetime.now().strftime('%H:%M:%S'),
                "device_id": "ESP32_Greenhouse",
                "devices": data.get('devices', {"vent": False, "fan": False, "heater": False, "light": False, "pump": False})
            }
            
            current_data.update(processed_data)
            
            history.append({
                "timestamp": datetime.now().isoformat(),
                "temperature": processed_data['temperature'],
                "humidity": processed_data['humidity'],
                "soil_moisture": processed_data['soil_moisture']
            })
            
            if len(history) > MAX_HISTORY:
                history.pop(0)
            
            print(f" Обработано: {processed_data}")
            return jsonify({"status": "success", "message": "Данные получены"})
            
    except Exception as e:
        print(f" Ошибка обработки данных: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400
    
    return jsonify({"status": "no data"}), 400


@app.route('/api/sensors', methods=['GET'])
def get_sensors():
    return jsonify(current_data)


@app.route('/api/history', methods=['GET'])
def get_history():
    recent_history = history[-20:] if len(history) > 20 else history
    return jsonify(recent_history)


@app.route('/api/test', methods=['GET'])
def test_data():
    import random
    from datetime import datetime
    
    test_data = {
        "temperature": round(20 + random.random() * 15, 1),
        "humidity": round(40 + random.random() * 40, 1),
        "soil_moisture": random.randint(0, 4095),
        "light_level": random.randint(0, 4095),
        "last_update": datetime.now().strftime('%H:%M:%S'),
        "device_id": "TEST_ESP32"
    }
    
    current_data.update(test_data)
    
    history.append({
        "timestamp": datetime.now().isoformat(),
        "temperature": test_data['temperature'],
        "humidity": test_data['humidity'],
        "soil_moisture": test_data['soil_moisture']
    })
    
    if len(history) > MAX_HISTORY:
        history.pop(0)
    
    return jsonify({"status": "success", "data": test_data})


@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


@app.route('/api')
def api_root():
    return jsonify({
        "name": "Умная Теплица API",
        "version": "1.0.0",
        "endpoints": {
            "/": "Главная страница",
            "/api/sensors": "Текущие данные с датчиков (GET)",
            "/api/data": "Отправка данных от ESP32 (POST)",
            "/api/history": "История показаний (GET)",
            "/api/test": "Тестовые данные (GET)",
            "/health": "Проверка состояния сервера (GET)"
        }
    })

# Точка входа для Gunicorn
application = app
