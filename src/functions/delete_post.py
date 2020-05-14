import json
import os

import boto3
import botocore

import api_responses


POST_TABLE_NAME = os.environ['DYNAMODB_POST_TABLE']
ERROR_MESSAGE = 'An error occured when saving the post to the database'
NO_POST_ERROR_MESSAGE = 'No post with such id'


def delete_post(event, context):
    dynamodb = boto3.resource('dynamodb')
    post_table = dynamodb.Table(POST_TABLE_NAME)
    data = json.loads(event['body'])
    user_uuid = data['user_uuid']
    post_id = data['post_id']

    try:
        post = post_table.get_item(
            Key={
                'user_uuid': user_uuid,
                'post_id': post_id
            }
        )
        if 'Item' not in post:
            return api_responses.get_error_response(400, NO_POST_ERROR_MESSAGE)

        post_table.delete_item(
            Key={
                'user_uuid': user_uuid,
                'post_id': post_id
            }
        )        
        return api_responses.get_success_response(204)
    except botocore.exceptions.ClientError as error:
        print(ERROR_MESSAGE)
        print(str(error))
        return api_responses.get_error_response(500, ERROR_MESSAGE)
