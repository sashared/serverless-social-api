import json
import os

import boto3
import botocore

import api_responses

def unfollow_user(event, context):
    dynamodb = boto3.resource('dynamodb')
    user_following_table = dynamodb.Table(os.environ['DYNAMODB_USERFOLLOWING_TABLE'])
    user_table = dynamodb.Table(os.environ['DYNAMODB_USER_TABLE'])
    data = json.loads(event['body'])
    current_user_uuid = data['current_user_uuid']
    another_user_uuid = data['another_user_uuid']

    try:
        current_user = user_table.get_item(
            Key={
                'user_uuid': current_user_uuid
            }
        )
        if 'Item' not in current_user:
            return api_responses.get_error_response(400, 'No user with given current user id')
        
        another_user = user_table.get_item(
            Key={
                'user_uuid': another_user_uuid
            }
        )
        if 'Item' not in another_user:
            return api_responses.get_error_response(400, 'No user with given another user id')

        user = user_following_table.get_item(
            Key={
                'follower_uuid': current_user_uuid,
                'followed_uuid': another_user_uuid
            }
        )
        if 'Item' not in user:
            return api_responses.get_error_response(400, 'Not following anyway!')

        user_following_table.delete_item(
            Key={
                'follower_uuid': current_user_uuid,
                'followed_uuid': another_user_uuid
            }
        )        
        return api_responses.get_success_response(204)
    except botocore.exceptions.ClientError as error:
        error_message = 'An error occured when trying to unfollow user'
        print(error_message)
        print(str(error))
        return api_responses.get_error_response(500, error_message)

