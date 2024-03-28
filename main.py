from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

PUT_SUCCESS = {'message': 'PUT request processed successfully\n', 'code': 200}
POST_SUCCESS = {'message': 'POST request processed successfully\n', 'code': 200}
DELETE_SUCCESS = {'message': 'DELETE request processed successfully\n', 'code': 200}

users_feedbacks = {}
users_feedbacks['user1'] = {}
users_feedbacks['user1']['post1'] = {'score': 5, 'comments': []}


@app.route("/")
def home():
    with open('modified_date.json', 'r') as f:
        data = json.load(f)
    return jsonify({"message": "Modified date: " + data['date']})


@app.route("/api/feedbacks", methods=["GET"])
def get_feedbacks():
    global users_feedbacks
    item_useruuid = request.args.get('useruuid', 'default_type')
    item_posttitle = request.args.get('posttitle', 'default_color')
    return jsonify({"message": users_feedbacks[item_useruuid][item_posttitle]['score']})


# # curl -X POST -H "Content-Type: application/json" -d '{"user": "neo4j", "password": "mUN8Mer61YTsqwBwDEaAbT7b6YeBFF4-ESwv81N7iK0", "uri": "neo4j+s://91476b49.databases.neo4j.io:7687"}' http://crystord:5000/api/create_element
# @app.route("/api/change_database", methods=["POST"])
# def change_database():
#     global ce
#     data = request.get_json()
#     user = data['user']
#     password = data['password']
#     uri = data['uri']
#     ce = crystord.ElementQuerier(user, password, uri)
#     return POST_SUCCESS['message'], POST_SUCCESS['code']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
