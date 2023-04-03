from flask import Flask, request, jsonify, session
from os import environ
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/test", methods=["POST"])
def show_query():
    
    print(request.is_json)
    print(request.get_json)

    if request.is_json:
        try:
            data = request.get_json()
            print(data)
        except Exception as e:
            return jsonify({
                "code": 500,
                "message": "place_order.py internal error"
            }), 500
        
    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
