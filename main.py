from flask import Flask, jsonify, request
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

PUT_SUCCESS = {'message': 'PUT request processed successfully\n', 'code': 200}
POST_SUCCESS = {'message': 'POST request processed successfully\n', 'code': 200}
DELETE_SUCCESS = {'message': 'DELETE request processed successfully\n', 'code': 200}

POST_FEEDBACKS_FILE_PATH = '/data/'


@app.route("/")
def home():
    with open('modified_date.json', 'r') as f:
        data = json.load(f)
    return jsonify({"message": "Modified date: " + data['date']})


# http://crystord:5001/api/get_post_feedback?posttitle=Reality%20Crushing%20Dreams&useruuid=1234
@app.route("/api/get_post_feedback", methods=["GET"])
def get_post_feedback():
    user_uuid = request.args.get('useruuid')
    post_title = request.args.get('posttitle')
    post_feedbacks = get_post_feedbacks_from_file(POST_FEEDBACKS_FILE_PATH + post_title + '.json')
    if post_feedbacks:
        message_data = {'post_average_score': post_feedbacks['post_data']['post_average_score'],
                        'post_ratings_number': post_feedbacks['post_data']['post_ratings_number'],
                        'user_score': post_feedbacks['users'][user_uuid]['score'],
                        'user_comments': post_feedbacks['users'][user_uuid]['comments']}
    else:
        message_data = {}
    return jsonify({"message": message_data})


# curl -X POST -H "Content-Type: application/json" -d '{"user_uuid": "1234", "post_title": "Reality Crushing Dreams", "user_score": 10}' http://crystord:5001/api/change_user_score
@app.route("/api/change_user_score", methods=["POST"])
def change_user_score():
    data_income = request.get_json()
    user_uuid = data_income['user_uuid']
    post_title = data_income['post_title']
    user_score = data_income['user_score']

    post_feedbacks = get_post_feedbacks_from_file(POST_FEEDBACKS_FILE_PATH + post_title + '.json')
    post_feedbacks = handle_empty_data_feedbacks(post_feedbacks, post_title, user_uuid)
    post_feedbacks = update_feedbacks_according_to_user_input(post_feedbacks, user_uuid, user_score)

    save_post_feedbacks_to_file(post_feedbacks)

    return POST_SUCCESS['message'], POST_SUCCESS['code']


# Private methods
def get_post_feedbacks_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data


def handle_empty_data_feedbacks(post_feedbacks, post_title, user_uuid):
    post_feedbacks = handle_empty_post_feedbacks(post_feedbacks, post_title, user_uuid)
    post_feedbacks = handle_empty_user_feedbacks(post_feedbacks, user_uuid)
    return post_feedbacks


def handle_empty_post_feedbacks(post_feedbacks, post_title, user_uuid):
    if not post_feedbacks:
        post_feedbacks = {'post_data': {'post_title': post_title, 'post_ratings_number': 0, 'post_average_score': 0}, 'users': {}}
    return post_feedbacks


def handle_empty_user_feedbacks(post_feedbacks, user_uuid):
    if user_uuid not in post_feedbacks['users']:
        post_feedbacks['users'][user_uuid] = {'score': 0, 'comments': []}
    return post_feedbacks


def update_feedbacks_according_to_user_input(post_feedbacks, user_uuid, user_score):
    post_feedbacks = update_user_score(post_feedbacks, user_uuid, user_score)
    post_feedbacks = update_ratings_number(post_feedbacks)
    post_feedbacks = update_post_average_score(post_feedbacks, user_uuid)
    return post_feedbacks


def update_user_score(post_feedbacks, user_uuid, user_score):
    if has_user_voted(post_feedbacks, user_uuid):
        post_feedbacks['users'][user_uuid]['score'] = user_score
    else:
        post_feedbacks['users'][user_uuid] = {'score': user_score, 'comments': []}
    return post_feedbacks


def has_user_voted(post_feedbacks, user_uuid):
    return user_uuid in post_feedbacks['users']


def update_ratings_number(post_feedbacks):
    post_feedbacks['post_data']['post_ratings_number'] = len(post_feedbacks['users'])
    return post_feedbacks


def update_post_average_score(post_feedbacks, user_uuid):
    avg_score = (sum([post_feedbacks['users'][user_uuid]['score'] for user_uuid in post_feedbacks['users']]) /
                 len(post_feedbacks['users']))
    post_feedbacks['post_data']['post_average_score'] = avg_score
    return post_feedbacks


def save_post_feedbacks_to_file(post_feedbacks):
    file_name = POST_FEEDBACKS_FILE_PATH + post_feedbacks['post_data']['post_title'] + '.json'
    with open(file_name, 'w') as file:
        json.dump(post_feedbacks, file)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
