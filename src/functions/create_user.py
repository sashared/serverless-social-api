import json
import uuid
import os

import boto3
import botocore

import api_responses

def create_user(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_USER_TABLE'])
    data = json.loads(event['body'])
    user_uuid = str(uuid.uuid4())
    name = data['name']
    email = data['email']
    address = data['address']

    try:
        table.put_item(
            Item={
                'user_uuid': user_uuid,
                'name': name,
                'email': email,
                'address': address,
            }
        )
        return api_responses.get_success_response(201, user_uuid)
    except botocore.exceptions.ClientError as error:
        error_message = 'An error occured when saving the user to the database'
        print(error_message)
        print(str(error))
        return api_responses.get_error_response(500, error_message)
