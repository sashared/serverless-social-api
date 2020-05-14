import json
import os

import boto3
import botocore

import api_responses

def delete_post(event, context):
    dynamodb = boto3.resource('dynamodb')
    post_table = dynamodb.Table(os.environ['DYNAMODB_POST_TABLE'])
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
            return api_responses.get_error_response(400, 'No post with such id')

        post_table.delete_item(
            Key={
                'user_uuid': user_uuid,
                'post_id': post_id
            }
        )        
        return api_responses.get_success_response(204)
    except botocore.exceptions.ClientError as error:
        error_message = 'An error occured when deleting the post from the database'
        print(error_message)
        print(str(error))
        return api_responses.get_error_response(500, error_message)
