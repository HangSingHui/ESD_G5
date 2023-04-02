from flask import Flask, request, jsonify
from os import environ
from flask_cors import CORS

app = Flask(__name__)


@app.route("/test")
def show_query():
    if request.is_json:
        try:
            details = request.get_json()
            print(details)
        except Exception as e:






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
