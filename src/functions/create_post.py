import json
import uuid
import os

import boto3
import botocore

import api_responses


USER_TABLE_NAME = os.environ['DYNAMODB_USER_TABLE']
POST_TABLE_NAME = os.environ['DYNAMODB_POST_TABLE']
ERROR_MESSAGE = 'An error occured when saving the post to the database'
NO_USER_ERROR_MESSAGE = 'No user with such id'


def create_post(event, context):
    dynamodb = boto3.resource('dynamodb')
    post_table = dynamodb.Table(POST_TABLE_NAME)
    user_table = dynamodb.Table(USER_TABLE_NAME)
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
            return api_responses.get_error_response(400, NO_USER_ERROR_MESSAGE)

        post_table.put_item(
            Item={
                'user_uuid': user_uuid,
                'post_id': post_id,
                'post': post
            }
        )
        return api_responses.get_success_response(201, post_id)
    except botocore.exceptions.ClientError as error:
        print(ERROR_MESSAGE)
        print(str(error))
        return api_responses.get_error_response(500, ERROR_MESSAGE)
