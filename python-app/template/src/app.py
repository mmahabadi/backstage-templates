from flask import Flask, jsonify
from datetime import datetime
import socket

app = Flask(__name__)

@app.route("/api/v1/details")
def details():
    return jsonify({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "status": "up",
        "message": "You are doing great!",
        'env': '${{ values.app_env }}',
        'app_name': '${{ values.app_name }}'
    })

@app.route("/api/v1/healthz")
def healthz():
    return jsonify({
        "status": "healthy"
    }), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0")
