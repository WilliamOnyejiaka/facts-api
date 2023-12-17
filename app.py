from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import json
import random


app = Flask(__name__)

app.config.from_mapping(
    SECRET_KEY="SECRET_KEY",

)

CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": {
            "*",
        }
    }
})

redis_client = redis.Redis(host="127.0.0.1", port=6379)

internal_server_error = {
    'error': True,
    'message': "something went wrong"
}


@app.post("/admin/add-facts")
def add_facts():
    file = request.files.get('file', None)
    data = json.load(file.stream)
    file.stream.close()

    for index, fact in enumerate(data['facts']):
        redis_client.lpush("facts", fact)

    return jsonify({
        'error': False,
        'message': "facts has been added successfully"
    }), 201


@app.get("/admin/details")
def db_details():

    try:
        facts_length = redis_client.llen('facts')
    except Exception as e:
        print(e)
        return jsonify(internal_server_error), 500

    return jsonify({
        'error': False,
        'details': {
            'facts-length': facts_length
        }
    }), 200


@app.get("/fact")
def get_fact():
    try:
        facts_length = redis_client.llen('facts')
        random_index = random.randint(0, facts_length-1)
        fact: str = (redis_client.lindex('facts', random_index)).decode('utf-8')
    except Exception as e:
        print(e)
        return jsonify(internal_server_error), 500

    print(fact)
    return jsonify({
        'error': False,
        'fact': fact[0].upper() + fact[1:]
    }),200
    

@app.get("/fact/<length>")
def get_facts(length):    
    try:
        facts_length = redis_client.llen('facts')
        facts: list = []
        
        for index in range(int(length)):
            random_index = random.randint(0, facts_length-1)
            fact: str = (redis_client.lindex('facts', random_index)).decode('utf-8')
            
            facts.append(fact[0].upper() + fact[1:])
        
        return jsonify({
            'error': False,
            'facts': facts 
        }),200
        
    except ValueError as e:
        return jsonify({
            'error': True,
            'message': "an integer is required"
        }),400
    except Exception as e:
        print(e)
        return jsonify(internal_server_error), 500



if __name__ == "__main__":
    app.run(debug=True)
