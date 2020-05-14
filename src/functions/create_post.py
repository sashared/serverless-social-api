import json
import uuid
import os

import boto3
import botocore

import api_responses

def create_post(event, context):
    dynamodb = boto3.resource('dynamodb')
    post_table = dynamodb.Table(os.environ['DYNAMODB_POST_TABLE'])
    user_table = dynamodb.Table(os.environ['DYNAMODB_USER_TABLE'])
    data = json.loads(event['body'])
    post_id = str(uuid.uuid4())
    user_uuid = data['user_uuid']
    post = data['post']

    try:
        user = user_table.get_item(
            Key={
                'user_uuid': user_uuid
            }
        )
        if 'Item' not in user:
            return api_responses.get_error_response(400, 'No user with such id')

        post_table.put_item(
            Item={
                'user_uuid': user_uuid,
                'post_id': post_id,
                'post': post
            }
        )
        return api_responses.get_success_response(201, post_id)
    except botocore.exceptions.ClientError as error:
        error_message = 'An error occured when saving the post to the database'
        print(error_message)
        print(str(error))
        return api_responses.get_error_response(500, error_message)
