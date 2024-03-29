from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

PUT_SUCCESS = {'message': 'PUT request processed successfully\n', 'code': 200}
POST_SUCCESS = {'message': 'POST request processed successfully\n', 'code': 200}
DELETE_SUCCESS = {'message': 'DELETE request processed successfully\n', 'code': 200}

USER_FEEDBACKS_FILE_PATH = '/data/'


@app.route("/")
def home():
    with open('modified_date.json', 'r') as f:
        data = json.load(f)
    return jsonify({"message": "Modified date: " + data['date']})


# http://crystord:5001/api/feedbacks?useruuid=1234&posttitle="Reality Crushing Dreams"
@app.route("/api/feedbacks", methods=["GET"])
def get_feedbacks():
    user_uuid = request.args.get('useruuid')
    post_title = request.args.get('posttitle')
    data_store = get_userdata_from_file(USER_FEEDBACKS_FILE_PATH + user_uuid + '.json')

    return jsonify({"message": data_store[post_title] if post_title in data_store else {}})


# curl -X POST -H "Content-Type: application/json" -d '{"user_uuid": "1234", "post_title": "Reality Crushing Dreams", "score": 10}' http://crystord:5001/api/change_user_score
@app.route("/api/change_user_score", methods=["POST"])
def change_user_score():
    data_income = request.get_json()
    user_uuid = data_income['user_uuid']
    post_title = data_income['post_title']
    user_score = data_income['score']

    file_name = USER_FEEDBACKS_FILE_PATH + user_uuid + '.json'
    data_store = get_userdata_from_file(file_name)
    data_store[post_title] = {'score': user_score}
    save_userdata_to_file(file_name, data_store)

    return POST_SUCCESS['message'], POST_SUCCESS['code']


def get_userdata_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


def save_userdata_to_file(file_name, data):
    with open(file_name, 'w') as file:
        json.dump(data, file)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
